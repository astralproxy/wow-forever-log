# wow-forever-log

A lightweight browser-based checklist tracker for personal adventure progress in WoW: Forever. The page reads structured data from a Google Sheet, lets users filter/sort entries, tracks progress in local storage, and opens a detailed panel for zone, dungeon, or raid objectives.

Live site: https://astralproxy.github.io/wow-forever-log/

Source data: https://docs.google.com/spreadsheets/d/e/2PACX-1vRU-_BIg8I_1cQ_qpPiITnKqzS85OUld4FApUi7j16KYFHuvz1Px3xuZuyfsd_dz6MoJqpASTzcgjGH/pubhtml

## Overview

This project is a static front-end app built with HTML, CSS, and a single embedded JavaScript section. It is designed to be easy to deploy and easy to update by editing the data source rather than the app itself.

The app does a few core things:

- Loads content from a spreadsheet-backed data source
- Groups entries into Dungeons, Raids, and Zones
- Allows filtering by level, category, and search text
- Tracks checked items using browser localStorage
- Shows quest and boss progress in a table and a side detail panel
- Sorts rows by level or zone name

## This README is the source of truth

This document is intended to preserve the project’s intent, structure, and behavior for future sessions when the current coding context may no longer be available.

If you need to re-establish the project quickly, rely on the following facts:

- Primary app entry: `index.html`
- Styling: `style.css`
- No build system or package manager is required for normal use
- Data is fetched from Google Sheets using the spreadsheet ID and CSV endpoints
- Progress is persisted in the browser via `localStorage`
- The app is a single-page checklist UI, not a server-rendered or framework-driven application
- The project is meant to be human-maintained, spreadsheet-driven, and lightweight

## Key files and responsibilities

- `index.html`
  - Contains the page layout, the filter controls, the table rendering logic, and the embedded JavaScript behavior.
  - Includes the main data-fetching code, sorting logic, localStorage updates, and detail panel rendering.

- `style.css`
  - Defines the visual layout, sidebar, table styling, badges, detail panel, and responsive behavior.

- `images/`
  - Stores static image assets used by detail panel entries.

## Important implementation details

- The app loads the main checklist from the API URL and separately loads Dungeons, Raids, and Zones tabs from the spreadsheet.
- Each detail tab is parsed into a lookup map keyed by the entry name to support quick retrieval when a row is selected.
- The table and detail panel both rely on stable IDs generated from the item name, which must stay consistent for progress tracking.
- Every checked row or sub-item is saved in localStorage with a key based on its entity and checklist type.
- Progress in the table is calculated by counting how many quest or boss items are marked complete for that entry.
- Sorting logic treats level values as numbers where possible, while still tolerating values like `?`.

## Code evaluation

### What the code does well

- Simple, portable architecture: it works as a static site with no framework or build step.
- Good use of localStorage for persistence, so progress remains after refresh.
- Separate data loading for the main table and detailed tabs keeps the UI flexible.
- CSV parsing is reasonably robust for basic spreadsheet data with quoted fields.
- A clear table/detail panel pattern makes the checklist easy to scan and update.

### Things to keep in mind

- The app is tightly coupled into one HTML file, so long-term maintenance may become harder as the project grows.
- Data is heavily dependent on spreadsheet structure and naming conventions.
- Some DOM values are inserted using template strings, so it is important to keep source data clean and sanitized.
- The script uses browser APIs directly, so it is best suited to a simple front-end workflow rather than a larger app architecture.

## High-level function overview

The JavaScript in the page is organized around a few main responsibilities:

- `loadSheetData()`
  - Fetches the main dataset plus the Dungeons, Raids, and Zones sheets.
  - Parses the spreadsheet content into lookup maps for detailed data.
  - Initializes filters and render state once the data is loaded.

- `parseCSV()`
  - Parses the CSV text into rows and cells while handling quoted values and line breaks correctly.
  - Converts spreadsheet text into usable JavaScript objects.

- `populateTypeFilterOptions()`
  - Builds any available type filter choices based on the current dataset.
  - Keeps the filter dropdown in sync with actual data values.

- `filterByCategory()`
  - Handles sidebar category navigation such as All Content, Dungeons, Raids, and Zones.
  - Updates active styling and re-applies the current filters.

- `applyFilters()`
  - Combines level, type, category, and search filters.
  - Produces the visible dataset shown in the table.
  - Re-sorts and re-renders after filtering changes.

- `checkLevelMatch()`, `checkSearchMatch()`, `checkSingleLevelValueMatch()`
  - Validate whether an item matches level-based automation and text search logic.
  - Support ranges like 1-10, 11-20, and single values such as 60.

- `renderTable()`
  - Builds the checklist table rows from the filtered data.
  - Creates the checkbox state, category tags, and progress summary for each row.
  - Applies the progress column visibility toggle.

- `openDetails()`
  - Opens the details panel for a selected zone, dungeon, or raid.
  - Pulls the matching record from the lookup maps and formats the detail content.
  - Shows additional quest and boss checklist data.

- `renderListWithCheckboxes()`
  - Converts raw quest or boss text into clickable checklist items with persistent localStorage state.
  - Marks each item as completed or incomplete in the detail panel.

- `toggleCheck()`
  - Saves a row-level completion state to localStorage.
  - Adds or removes the completed styling for the table row.

- `toggleDetailCheck()`
  - Saves completion state for quest or boss detail items.
  - Updates the detail item styling and refreshes the progress summary in the table.

- `closePanel()`
  - Closes the detail side panel and removes the mobile overlay backdrop if present.

- `sortTable()`, `sortDataArray()`, `getColumnValue()`
  - Handle table sorting by column and direction.
  - Keep numeric sorting behavior sensible for level values and optional unknown values.

- `getItemProgress()` and `countCategoryProgress()`
  - Calculate how many quest and boss items are done for a given entity.
  - Return a compact progress summary displayed in the table.

- `toggleProgressColumn()`
  - Shows or hides the progress column based on the user checkbox in the filter bar.

- `escapeHtml()`
  - Sanitizes strings before inserting them into HTML to reduce the risk of malformed markup or unsafe output.

## Data schema

The app expects a spreadsheet structure with a few standard fields in each row. The main checklist data comes from the API response and is read as objects like `level`, `zone`, `type`, and optional note fields. The detail tabs (Dungeons, Raids, Zones) are parsed as CSV rows and mapped by the entry name.

### Main checklist data

Each row in the main dataset is expected to provide the following information:

- `level`
  - The numeric or range-based level for the row.
  - Used by the level filter and sorting logic.

- `zone`
  - The display name of the zone, dungeon, or raid entry.
  - This becomes the primary key for matching the main table row to the detail data.

- `type`
  - The category label for the item, such as a dungeon or raid type.
  - Affects category filtering and the row’s tag styling.

- `cellNotes` or note-like metadata
  - Optional notes stored on the item.
  - Used for tooltips and additional context in the main table.

### Detail tab schema (Dungeons / Raids / Zones)

Each detail tab is parsed as CSV with one entry per row. The app reads the row in this order:

1. `level`
   - The entry level or level range.

2. `name`
   - The display name of the dungeon, raid, or zone.
   - This is used as the lookup key after trimming and lowering case.

3. `location`
   - The region or area name associated with the entry.
   - Displayed in the detail panel and used as a note source.

4. `quests`
   - A newline-delimited list of quest objectives.
   - Rendered as checklist items in the details panel.

5. `bosses`
   - A newline-delimited list of boss names or objectives.
   - Rendered as checklist items in the details panel.

6. `image` or column 7 in the sheet
   - The image identifier used to construct the filename for a preview image in the details panel.
   - The code reads the value from the 7th CSV column and appends it to `images/<name>.webp`.

### Important assumptions

- The sheet content must remain relatively stable in column order.
- The `zone` value in the main dataset should match the `name` value in the detail tab for the same entry.
- The app assumes quest and boss data are stored as multi-line text values so they can be split by newline.
- Any row missing a `zone` is ignored in the main list rendering.

## Typical data flow

1. The page loads and fetches data from the spreadsheet-backed API and detail tabs.
2. Each tab is parsed into a lookup map keyed by entry name.
3. The main dataset is filtered and sorted based on the active view.
4. The rendered table shows progress and clickable links to the detail pane.
5. User actions update localStorage, so progress persists between reloads.

## Summary

This project is a practical, low-overhead checklist app for tracking WoW: Forever content. The code is simple, readable, and effective for a small static site, with the main strengths being persistence, spreadsheet-driven data, and clean user interaction flows.
