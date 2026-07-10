-- rules.lua
--
-- API reference documents need two visually distinct separators:
--   - a THICK rule between namespaces (classes, top-level modules, ...)
--   - a THIN rule between members (functions, attributes, ...) and their
--     member-summary tables.
--
-- Author markup (same in every source file, regardless of target format):
--
--     ::: {.namespace-rule}
--     :::
--
--     ::: {.member-rule}
--     :::
--
-- These are emitted by the API-doc generator (scripts/gen_api_docs.py) but
-- are just as valid hand-written in any regular page.

local FORMAT = FORMAT

local TYPST_THICK = "#line(length: 100%, stroke: 1.6pt)"
local TYPST_THIN  = "#line(length: 100%, stroke: 0.4pt + gray)"

local HTML_THICK = '<hr class="namespace-rule">'
local HTML_THIN  = '<hr class="member-rule">'

-- Explicit, author-placed page-break hint -- the deterministic alternative
-- to trying to auto-detect "too close to the bottom of the page" (which
-- Typst can't do reliably; see the long comment in template/manual.typst
-- for why). Write this in markdown right before whatever should start a
-- fresh page:
--
--     ::: {.pagebreak-before}
--     :::
--
--     ## The section that should start clean
--
-- Ignored (returns nothing) for CommonMark/Docusaurus, since Docusaurus
-- pages don't have a fixed page size for this to mean anything -- and for
-- HTML we emit a CSS page-break hint instead, which only has any effect
-- when the page is printed to PDF from the browser.
local function handle_pagebreak_marker(el, isPagebreak)
  if not isPagebreak then return nil end
  if FORMAT == "typst" then
    return pandoc.RawBlock("typst", "#pagebreak(weak: true)")
  elseif FORMAT:match("html") then
    return pandoc.RawBlock("html", '<div style="break-before: page;"></div>')
  end
  return {} -- commonmark and anything else: no-op, drop the empty div
end

function Div(el)
  local isNamespace = el.classes:includes("namespace-rule")
  local isMember     = el.classes:includes("member-rule")

  if (isNamespace or isMember) then
    if FORMAT == "typst" then
      local raw = isNamespace and TYPST_THICK or TYPST_THIN
      return pandoc.RawBlock("typst", raw)
    elseif FORMAT:match("html") then
      local raw = isNamespace and HTML_THICK or HTML_THIN
      return pandoc.RawBlock("html", raw)
    elseif FORMAT:match("commonmark") or FORMAT:match("markdown") then
      -- Raw HTML block passes straight through CommonMark/Docusaurus (MDX
      -- renders bare <hr> tags fine) and still degrades to *** in editors
      -- that don't render raw HTML if you ever inspect the source directly.
      local raw = isNamespace and HTML_THICK or HTML_THIN
      return pandoc.RawBlock("html", raw)
    end
  end

  local isPagebreak  = el.classes:includes("pagebreak-before")
  if isPagebreak then
    return handle_pagebreak_marker(el, true)
  end

  return nil -- unknown format: leave the empty div as-is rather than guess
end

-- function Span(el)
--   local id = el.identifier
--   if id ~= "" and #el.content == 0 then
--     if FORMAT == "typst" then
--       return pandoc.RawInline("typst", '#label("' .. id .. '")')
--     elseif FORMAT:match("commonmark") then
--       return pandoc.RawInline("html", '<a id="' .. id .. '"></a>')
--     end
--   end
-- end