-- crosslink.lua
--
-- Authors always write cross-file links the same way, regardless of which
-- output the docs eventually become:
--
--     See [the setup guide](../guides/getting-started.md#install-the-cli).
--
-- How that link needs to render depends on the target:
--
--   crosslink_mode = "internal"      (single Pandoc pass -> one Typst doc,
--                                      or one monolithic HTML page)
--                    -> strip the file path, keep only `#install-the-cli`
--                       so it becomes an in-document reference.
--
--   crosslink_mode = "html-multipage" (each file rendered to its own .html)
--                    -> keep the relative path, swap the extension for
--                       .html so the browser follows it to the sibling page.
--
--   crosslink_mode = "commonmark" (or unset)
--                    -> leave the link exactly as written; Docusaurus
--                       resolves relative .md links itself.
--
-- Pass the mode in with, e.g.:
--   pandoc -M crosslink_mode=internal ...

local mode = "commonmark"

local function is_external(target)
  return target:match("^%a[%w+.-]*://") -- scheme:// (http, https, mailto is handled below)
      or target:match("^mailto:")
      or target:match("^#") -- already a same-file fragment; nothing to do
end

local function rewrite(target)
  if is_external(target) then
    return target
  end

  -- split "path/to/file.md#anchor" (anchor optional)
  local path, anchor = target:match("^([^#]*)#?(.*)$")
  if not path or path == "" then
    return target -- pure "#anchor", already handled by is_external above; safety net
  end
  if not path:match("%.mdx?$") then
    return target -- not a link into another markdown source file; leave alone
  end

  if mode == "internal" then
    if anchor ~= "" then
      return "#" .. anchor
    end
    -- No anchor was given for a cross-file link in a monolithic build: we
    -- cannot resolve "the top of that file" as a Typst label, so surface it
    -- loudly instead of silently producing a dead link.
    io.stderr:write(
      "crosslink.lua: WARNING - link to '" .. path ..
      "' has no #anchor and mode=internal; leaving as external string link\n"
    )
    return target
  elseif mode == "html-multipage" then
    local htmlPath = path:gsub("%.mdx?$", ".html")
    if anchor ~= "" then
      return htmlPath .. "#" .. anchor
    end
    return htmlPath
  else
    return target -- commonmark / docusaurus: pass through untouched
  end
end

local function Link(el)
  el.target = rewrite(el.target)
  return el
end

-- IMPORTANT: Pandoc's Lua filter traversal visits body elements in document
-- order, which happens *before* a bare top-level `Meta` handler would run
-- (Meta and the block tree are sibling fields of the Pandoc element, and the
-- default single-file walk hits Link nodes first). Reading `mode` from a
-- `Meta` handler is therefore too late for the first links in the document.
-- Using an explicit `Pandoc(doc)` entry point lets us read metadata *before*
-- walking the blocks, so ordering is guaranteed regardless of pandoc version.
function Pandoc(doc)
  if doc.meta.crosslink_mode then
    mode = pandoc.utils.stringify(doc.meta.crosslink_mode)
  end
  -- Pipeline-internal bookkeeping, not content: strip it so it never shows
  -- up as a stray key in rendered frontmatter (this matters most for the
  -- CommonMark/Docusaurus target, since --standalone dumps the full
  -- metadata map back out as a YAML frontmatter block).
  doc.meta.crosslink_mode = nil
  doc.blocks = pandoc.walk_block(pandoc.Div(doc.blocks), { Link = Link }).content
  return doc
end
