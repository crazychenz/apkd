-- toc-control.lua
--
-- Lets an author write:
--
--     ## A heading that should still show in the doc, but not clutter the TOC {.unlisted}
--     ## A heading with no outline entry AND no section number {.unlisted .unnumbered}
--
-- Pandoc's HTML writer already honors `.unlisted` for --toc and `.unnumbered`
-- for numbering, natively, so we leave HTML/CommonMark alone.
--
-- Pandoc's Typst writer, however, does NOT translate these classes into the
-- Typst-native `outlined:` / `numbering:` heading parameters, so for the
-- `typst` target we rewrite the Header into an explicit raw Typst
-- `#heading(...)` call, then re-emit the identifier as a label on the
-- following line -- exactly mirroring the pattern Pandoc itself uses for
-- ordinary headings (`== Text` followed by `<label>`), so cross references
-- via `[text](#identifier)` keep working unchanged.

local FORMAT = FORMAT

-- Escape characters Typst treats as markup inside a #heading(...)[body]
-- content block. We keep it conservative: Pandoc has already fully resolved
-- inline formatting (emphasis, code, links, etc.) by the time this filter
-- runs *if* we render the inlines with pandoc.write, so this function is
-- only used as a fallback for the plain-text identifier/level bookkeeping.
local function inlines_to_typst(inlines)
  local doc = pandoc.Pandoc({ pandoc.Plain(inlines) })
  local rendered = pandoc.write(doc, "typst")
  -- pandoc.write appends a trailing newline; strip it.
  return rendered:gsub("%s+$", "")
end

function Header(el)
  local unlisted  = el.classes:includes("unlisted")
  local unnumbered = el.classes:includes("unnumbered")

  if not (unlisted or unnumbered) then
    return nil -- ordinary heading, let the native writer do its thing
  end

  if FORMAT:match("commonmark") then
    -- Docusaurus's custom-heading-id parser expects exactly `{#id}` with no
    -- other attributes; strip our bookkeeping classes but keep the id so
    -- the anchor still resolves. TOC-exclusion itself isn't representable
    -- in plain CommonMark/Docusaurus sidebars, so this is a documented
    -- limitation (see README) rather than something a filter can fix.
    el.classes = pandoc.List({})
    return el
  end

  if FORMAT ~= "typst" then
    return nil -- html (and anything else): native writer already handles it
  end

  local body = inlines_to_typst(el.content)
  local params = { "level: " .. tostring(el.level) }
  if unlisted then
    params[#params + 1] = "outlined: false"
  end
  if unnumbered then
    params[#params + 1] = "numbering: none"
  end

  local raw = "#heading(" .. table.concat(params, ", ") .. ")[" .. body .. "]"
  if el.identifier and el.identifier ~= "" then
    raw = raw .. "\n<" .. el.identifier .. ">"
  end

  return { pandoc.RawBlock("typst", raw) }
end
