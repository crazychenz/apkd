-- number-headings-markdown.lua
--
-- Numbers headings manually, but ONLY when the output format is
-- Markdown/CommonMark/GFM. HTML, LaTeX, and Typst already get their
-- numbers natively from pandoc's --number-sections, so this filter
-- stays out of the way for those targets to avoid double-numbering.
--
-- SUPPORTS A FILE THAT STARTS AT ANY HEADING LEVEL:
-- Numbering is relative to whatever level the file's first heading
-- uses, not to absolute levels 1-6, so a file starting at `##` numbers
-- its first heading "1" (not "0.1") by default.
--
-- OPTIONAL STARTING NUMBER:
-- Set a `first-section-number` field in the YAML frontmatter, e.g.
--   first-section-number: "2.1"
-- to make the file's first heading come out as "2.1" instead of "1",
-- with every following heading (at any level) continuing to increment
-- normally from that point. Only the LAST component of the given
-- number is ever incremented for sibling headings; earlier components
-- (representing ancestor sections not physically present in this file)
-- stay fixed.
--
-- FRONTMATTER TITLE SYNC:
-- If a heading's original text exactly matches the frontmatter
-- `title`, the frontmatter title is rewritten to include that same
-- section number, so a heading that was deliberately duplicated into
-- the frontmatter (e.g. for Docusaurus, which prefers frontmatter
-- title over the filename) stays in sync with its numbered heading.
--
-- Usage (safe to always include, for every format):
--   pandoc input.md --number-sections --lua-filter=number-headings-markdown.lua -o output.html
--   pandoc input.md --number-sections --lua-filter=number-headings-markdown.lua -o output.pdf --pdf-engine=typst
--   pandoc input.md --number-sections --lua-filter=number-headings-markdown.lua -s -t commonmark -o output.md

local function is_markdown_target()
  return FORMAT:match("commonmark") or FORMAT:match("^markdown") or FORMAT:match("gfm")
end

local function split_dotted(str)
  local parts = {}
  for piece in tostring(str):gmatch("[^.]+") do
    table.insert(parts, tonumber(piece) or piece)
  end
  return parts
end

function Pandoc(doc)
  if not is_markdown_target() then
    return doc
  end

  local seed = {}
  if doc.meta["first-section-number"] then
    seed = split_dotted(pandoc.utils.stringify(doc.meta["first-section-number"]))
  end
  local offset_len = math.max(#seed, 1)

  local counters = {}
  local base_level = nil
  local meta_title_str = doc.meta.title and pandoc.utils.stringify(doc.meta.title) or nil
  local matched_numbered_title = nil

  local function number_header(el)
    if el.classes:includes("unnumbered") then
      return el
    end

    local original_text = pandoc.utils.stringify(el)
    local level = el.level

    if base_level == nil then
      base_level = level
    end

    local idx = offset_len + (level - base_level)
    if idx < 1 then idx = 1 end

    if counters[idx] then
      counters[idx] = counters[idx] + 1
    else
      counters[idx] = seed[idx] or 1
    end

    -- deeper levels start fresh the next time they're reached
    for i = idx + 1, idx + 20 do
      counters[i] = nil
    end

    local parts = {}
    for i = 1, idx do
      table.insert(parts, tostring(counters[i] or seed[i] or 0))
    end
    local number = table.concat(parts, ".")

    table.insert(el.content, 1, pandoc.Space())
    table.insert(el.content, 1, pandoc.Str(number))

    if meta_title_str and original_text == meta_title_str and not matched_numbered_title then
      matched_numbered_title = number .. " " .. original_text
    end

    return el
  end

  doc.blocks = doc.blocks:walk({ Header = number_header })

  if matched_numbered_title then
    doc.meta.title = pandoc.MetaString(matched_numbered_title)
  end

  return doc
end