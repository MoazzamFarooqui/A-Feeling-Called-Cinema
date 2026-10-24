import fs from 'node:fs'
import path from 'node:path'
import puppeteer from 'puppeteer-core'

const EDGE =
  process.env.EDGE_PATH || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
const BASE = process.env.APP_URL || 'http://localhost:5173'
const SHOTS = process.env.SHOT_DIR || path.join(process.env.TEMP || '.', 'a-feeling-called-cinema-e2e')
const TIMEOUT = Number(process.env.E2E_TIMEOUT || 90000)

fs.mkdirSync(SHOTS, { recursive: true })

const pageErrors = []
const results = []

function assert(condition, message) {
  if (!condition) throw new Error(message)
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(SHOTS, name) })
}

async function goto(page, pathname) {
  await page.goto(BASE + pathname, { waitUntil: 'domcontentloaded' })
  await page.waitForSelector('.sidebar', { timeout: 20000 })
}

async function waitCards(page, minimum = 1) {
  await page.waitForFunction(
    (count) => document.querySelectorAll('.movie-grid .movie-card').length >= count,
    { timeout: TIMEOUT },
    minimum,
  )
  return page.$$eval('.movie-grid .movie-card', (cards) => cards.length)
}

async function waitResults(page, minimum = 1) {
  await new Promise((resolve) => setTimeout(resolve, 350))
  await page.waitForFunction(
    (count) =>
      !document.querySelector('.skeleton-card') &&
      document.querySelectorAll('.movie-grid .movie-card').length >= count,
    { timeout: TIMEOUT },
    minimum,
  )
  return page.$$eval('.movie-grid .movie-card', (cards) => cards.length)
}

async function pickMovie(page, index, title) {
  const pickers = await page.$$('.movie-picker')
  assert(pickers[index], `Movie picker #${index + 1} not found`)
  const input = await pickers[index].$('.picker-input')
  assert(input, `Movie picker #${index + 1} is already selected`)
  const selectedBefore = await page.$$eval('.picker-selected', (items) => items.length)
  await input.click()
  await input.type(title, { delay: 20 })
  await page.waitForSelector('.picker-option', { timeout: 20000 })
  const chosen = await page.$$eval(
    '.picker-option',
    (options, wanted) => {
      const match = options.find((option) =>
        option.textContent.toLowerCase().includes(wanted.toLowerCase()),
      )
      const target = match || options[0]
      if (!target) return null
      target.click()
      return target.textContent.trim()
    },
    title,
  )
  assert(chosen, `No suggestion found for "${title}"`)
  await page.waitForFunction(
    (count) => document.querySelectorAll('.picker-selected').length >= count,
    { timeout: 5000 },
    selectedBefore + 1,
  )
  return chosen
}

async function submit(page) {
  await page.click('.tool-panel form button[type="submit"]')
}

const browser = await puppeteer.launch({
  executablePath: EDGE,
  headless: true,
  args: ['--disable-gpu', '--no-first-run', '--no-default-browser-check'],
})

try {
  const page = await browser.newPage()
  await page.setViewport({ width: 1440, height: 1100 })
  page.on('console', (message) => {
    if (message.type() === 'error') pageErrors.push(`console: ${message.text()}`)
  })
  page.on('pageerror', (error) => pageErrors.push(`pageerror: ${error.message}`))

  console.log(`Screenshots: ${SHOTS}`)

  // 1. Mood search
  await goto(page, '/mood')
  await page.type('.mood-input', 'submarine thriller', { delay: 15 })
  await submit(page)
  const moodCount = await waitResults(page, 3)
  await shot(page, '01-mood-results.png')
  results.push(`Mood search: ${moodCount} results`)
  console.log(results.at(-1))

  // 2. Hidden gems with filters
  await goto(page, '/hidden-gems')
  await waitCards(page, 3)
  await page.select('#gem-genre', 'Drama')
  await page.type('#year-min', '1970')
  await page.type('#year-max', '2010')
  await submit(page)
  const gemCount = await waitResults(page, 1)
  await shot(page, '02-hidden-gems.png')
  results.push(`Hidden gems (Drama 1970-2010): ${gemCount} results`)
  console.log(results.at(-1))

  // 3. Watch party
  await goto(page, '/watch-party')
  const pickedA = await pickMovie(page, 0, 'Inception')
  const pickedB = await pickMovie(page, 1, 'Toy Story')
  await submit(page)
  const partyCount = await waitResults(page, 3)
  await shot(page, '03-watch-party.png')
  results.push(`Watch party (${pickedA} + ${pickedB}): ${partyCount} results`)
  console.log(results.at(-1))

  // 4. Time budget with finish clocks
  await goto(page, '/time-budget')
  await submit(page)
  const timeCount = await waitResults(page, 3)
  const hasFinishClock = await page.$$eval('.movie-card .meta-pill', (pills) =>
    pills.some((pill) => pill.textContent.includes('Ends')),
  )
  assert(hasFinishClock, 'Time budget cards are missing finish clocks')
  await shot(page, '04-time-budget.png')
  results.push(`Time budget: ${timeCount} results with finish clocks`)
  console.log(results.at(-1))

  // 5. Double feature playlist
  await goto(page, '/double-feature')
  await pickMovie(page, 0, 'Inception')
  await submit(page)
  const pairCount = await waitResults(page, 2)
  assert(pairCount === 2, `Double feature returned ${pairCount} movies instead of 2`)
  const pairTitles = await page.$$eval('.movie-grid .poster-title', (titles) =>
    titles.map((title) => title.textContent.trim()),
  )
  await shot(page, '05-double-feature.png')
  results.push(`Double feature: ${pairTitles.join(' + ')}`)
  console.log(results.at(-1))

  // 6. Cultural bridge (foreign-only badges)
  await goto(page, '/cultural-bridge')
  await pickMovie(page, 0, 'Inception')
  await submit(page)
  const bridgeCount = await waitResults(page, 3)
  const languageBadges = await page.$$eval('.movie-grid .badge-lang', (badges) => badges.length)
  assert(languageBadges >= 3, 'Cultural bridge cards are missing language badges')
  await shot(page, '06-cultural-bridge.png')
  results.push(`Cultural bridge: ${bridgeCount} results, ${languageBadges} language badges`)
  console.log(results.at(-1))

  // 7. Era machine (all results in selected decade)
  await goto(page, '/era-machine')
  await pickMovie(page, 0, 'Inception')
  await page.select('#decade', '1980')
  await submit(page)
  const eraCount = await waitResults(page, 3)
  const allEighties = await page.$$eval('.movie-grid .poster-sub', (subs) =>
    subs.every((sub) => /\(?198\d\)?/.test(sub.textContent) || /198\d/.test(sub.textContent)),
  )
  assert(allEighties, 'Era machine returned films outside the 1980s')
  await shot(page, '07-era-machine.png')
  results.push(`Era machine (1980s): ${eraCount} results, all in decade`)
  console.log(results.at(-1))

  // 8. Movie detail modal
  await page.click('.movie-grid .movie-card')
  await page.waitForSelector('.modal-panel', { timeout: 5000 })
  const modalTitle = await page.$eval('.modal-panel h2', (element) => element.textContent.trim())
  await shot(page, '08-movie-modal.png')
  await page.keyboard.press('Escape')
  await page.waitForFunction(() => !document.querySelector('.modal-panel'), { timeout: 5000 })
  results.push(`Movie modal: opened for "${modalTitle}" and closed with Escape`)
  console.log(results.at(-1))

  // 9. Home live data
  await goto(page, '/')
  const homeGems = await waitCards(page, 3)
  await shot(page, '09-home.png')
  results.push(`Home: ${homeGems} live hidden-gem cards`)
  console.log(results.at(-1))

  assert(pageErrors.length === 0, `Browser console errors:\n${pageErrors.join('\n')}`)
  console.log('\nE2E PASSED')
} finally {
  await browser.close()
}
