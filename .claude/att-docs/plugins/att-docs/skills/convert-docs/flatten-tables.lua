-- Rewrites every table so it can be written as a Markdown pipe table.
--
-- Pipe tables are the only table syntax that renders outside Pandoc. A grid
-- table shows up in a Markdown viewer as one run-together paragraph of pluses
-- and pipes, and the writers that do not support grid tables replace the whole
-- table with the text [TABLE], which loses the contents outright.
--
-- Two things stop a Word table from being a pipe table, and both are fixed
-- here. A cell holding a list or several paragraphs is block content, which
-- pipe syntax cannot hold, so it is flattened to one line of text. A cell
-- spanning rows or columns has no pipe equivalent, so it is expanded into the
-- individual cells it covers, keeping the grid rectangular.

local List = require 'pandoc.List'

-- Whether the text so far already ends in punctuation that separates it from
-- what follows, so that a lead-in like "the following columns:" does not become
-- "the following columns:;".
local function ends_open(inlines)
  for i = #inlines, 1, -1 do
    local last = inlines[i]
    if last.t == 'Str' then
      local text = last.text
      return text:sub(-1):match('[:;,.%-]') == nil
    elseif last.t ~= 'Space' and last.t ~= 'SoftBreak' and last.t ~= 'LineBreak' then
      return true
    end
  end
  return false
end

local flatten_blocks

local function join(target, addition)
  if #addition == 0 then
    return target
  end
  if #target > 0 then
    if ends_open(target) then
      target:insert(pandoc.Str(';'))
    end
    target:insert(pandoc.Space())
  end
  target:extend(addition)
  return target
end

local function flatten_items(items)
  local out = List:new{}
  for _, item in ipairs(items) do
    out = join(out, flatten_blocks(item))
  end
  return out
end

-- Reduces a list of blocks to a single line of inlines, keeping every boundary
-- the reader needs: the items of a list stay separated, which is what makes
-- this worth writing rather than calling blocks_to_inlines, since that runs the
-- items of a list together into one word.
flatten_blocks = function(blocks)
  local out = List:new{}
  for _, block in ipairs(blocks) do
    local t = block.t
    if t == 'Para' or t == 'Plain' or t == 'Header' then
      out = join(out, List:new(block.content))
    elseif t == 'BulletList' or t == 'OrderedList' then
      local items = block.content
      if t == 'OrderedList' then
        items = block.content
      end
      out = join(out, flatten_items(items))
    elseif t == 'DefinitionList' then
      for _, entry in ipairs(block.content) do
        out = join(out, List:new(entry[1]))
        out = join(out, flatten_items(entry[2]))
      end
    elseif t == 'BlockQuote' or t == 'Div' then
      out = join(out, flatten_blocks(block.content))
    elseif t == 'LineBlock' then
      for _, line in ipairs(block.content) do
        out = join(out, List:new(line))
      end
    elseif t == 'CodeBlock' then
      out = join(out, List:new{pandoc.Code(block.text)})
    elseif t == 'RawBlock' then
      out = join(out, List:new{pandoc.Str(block.text)})
    elseif t ~= 'HorizontalRule' then
      out = join(out, List:new{pandoc.Str(pandoc.utils.stringify(block))})
    end
  end
  return out
end

-- A pipe table row is one line, so a line break inside a cell is what a Word
-- author pressed shift and enter for and pipe syntax cannot hold. Left in
-- place it forces the writer to fall back to HTML for the whole table.
local function strip_breaks(inlines)
  -- Walked as a block rather than looped over, so a break nested inside emphasis
  -- or a link is reached too.
  local plain = pandoc.walk_block(pandoc.Plain(inlines), {
    LineBreak = function(_) return pandoc.Space() end,
    SoftBreak = function(_) return pandoc.Space() end,
  })
  return plain.content
end

local function empty_cell()
  return pandoc.Cell({pandoc.Plain({})})
end

-- Expands the spanned cells of a set of rows so every row holds one cell per
-- column. A cell spanning columns leaves empty cells beside it; a cell spanning
-- rows leaves an empty cell in each row beneath it.
local function expand(rows, width)
  local out = List:new{}
  local carried = {}
  for _, row in ipairs(rows) do
    local cells = List:new{}
    local source = 1
    local column = 1
    while column <= width do
      if (carried[column] or 0) > 0 then
        carried[column] = carried[column] - 1
        cells:insert(empty_cell())
        column = column + 1
      elseif source <= #row.cells then
        local cell = row.cells[source]
        source = source + 1
        local across = math.max(1, cell.col_span)
        local down = math.max(1, cell.row_span)
        cell.col_span = 1
        cell.row_span = 1
        cell.contents = {pandoc.Plain(strip_breaks(flatten_blocks(cell.contents)))}
        cells:insert(cell)
        if down > 1 then
          carried[column] = down - 1
        end
        column = column + 1
        for _ = 2, across do
          if column > width then
            break
          end
          if down > 1 then
            carried[column] = down - 1
          end
          cells:insert(empty_cell())
          column = column + 1
        end
      else
        cells:insert(empty_cell())
        column = column + 1
      end
    end
    out:insert(pandoc.Row(cells, row.attr))
  end
  return out
end

function Table(tbl)
  local width = #tbl.colspecs
  if width == 0 then
    return tbl
  end

  -- The head, body and foot objects are mutated in place: this Lua API exposes
  -- no constructor for any of the three.
  local head_rows = expand(tbl.head.rows, width)
  for _, body in ipairs(tbl.bodies) do
    body.head = expand(body.head, width)
    body.body = expand(body.body, width)
    body.row_head_columns = 0
  end

  -- A pipe table has to open with a header row. A Word table that starts
  -- straight into its data leaves the header empty, so the first row of the
  -- body moves up into it.
  if #head_rows == 0 then
    for _, body in ipairs(tbl.bodies) do
      if #body.body > 0 then
        head_rows:insert(body.body:remove(1))
        break
      end
    end
  end

  tbl.head.rows = head_rows
  tbl.foot.rows = expand(tbl.foot.rows, width)
  return tbl
end
