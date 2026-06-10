# lobsterss overview

RSS and Atom feeds for [lobste.rs](https://lobste.rs), with filtering by score, comments, and keywords.

[TOC]

lobsterss wraps the lobste.rs JSON API and generates filtered RSS and Atom feeds on demand.
Feeds are cached for 20 minutes to be a good API citizen.

lobste.rs provides basic tag-based feeds but has no built-in way to filter by score, comment count,
or title keyword. lobsterss adds those as query parameters on top of the standard feed URLs.

## Base feeds

The following feeds mirror lobste.rs's own URLs and are available in RSS (`.rss`) and Atom (`.atom`) format.

| Feed                                    | URL                       |
|-----------------------------------------|---------------------------|
| Hottest                                 | `/hottest.rss`            |
| Newest                                  | `/newest.rss`             |
| By [tag](https://lobste.rs/tags)        | `/t/python.rss`           |
| Multiple [tags](https://lobste.rs/tags) | `/t/rust,python,java.rss` |

Multi-tag feeds use OR semantics - stories tagged with any of the listed tags are included.

## Filters

Append to any feed URL as query parameters.

| Parameter        | Description                          |
|------------------|--------------------------------------|
| `min_score=N`    | Stories with N or more score         |
| `min_comments=N` | Stories with N or more comments      |
| `q=term`         | Case-insensitive title keyword match |

The `q` parameter supports boolean operators:

- `?q=rust+OR+go` - titles containing "rust" or "go"
- `?q=async+AND+rust` - titles containing both "async" and "rust"
- `?q=C%2B%2B` - symbols work too

_Operators can't currently be combined, and a maximum of 5 terms are supported._

## Examples

- [`/hottest.rss?min_score=10&min_comments=2`](/hottest.rss?min_score=10&min_comments=2)
- [`/newest.rss?q=AI`](/newest.rss?q=AI)
- [`/t/ai.rss?q=model+OR+api&min_score=3`](/t/ai.rss?q=model+OR+api&min_score=3)
- [`/t/programming,compsci.atom?min_comments=3`](/t/programming,compsci.atom?min_comments=3)
