-- Removes the nodes that cannot survive the trip to plain Markdown.
--
-- Images go because the output is Markdown only, with no media extraction and
-- no _assets folder, so an image node would render as a link to a file that is
-- never written. The caption text of a Figure is worth keeping, so it is
-- unwrapped into an ordinary paragraph rather than discarded with the image.
--
-- Spans and divs go because Markdown has nothing to render them as. A Word
-- highlight or character style arrives as a Span, and left alone the writer
-- emits it as a raw <span class="mark"> that is neither Markdown nor anything
-- the reader needs. Unwrapping keeps the text and drops the wrapper. Doing it
-- here rather than over the finished text is what keeps the documents' own
-- angle brackets intact: these specifications write their placeholders as
-- <First Name> and quote XML payloads verbatim.

function Image(_)
  return {}
end

function Figure(fig)
  if fig.caption and fig.caption.long and #fig.caption.long > 0 then
    return fig.caption.long
  end
  return {}
end

function Span(span)
  return span.content
end

function Div(div)
  return div.content
end

-- Underline and small caps are their own node types rather than spans, and
-- Markdown can write neither, so the writer falls back to a raw
-- <span class="underline"> for them. The formatting is Word's and the words are
-- the document's, so the wrapper goes and the text stays.
function Underline(node)
  return node.content
end

function SmallCaps(node)
  return node.content
end
