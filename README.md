# SG Law Cookies Functions

This repo contains all the code/functions required to run the website.

## Email Support
Function necessary to run a simple newsletter

* Send Confirmation email
* Add member
* Unsubscribe
* Send newsletter

## Workflow

```mermaid
graph TD
    A[Scrape Articles] --"List(NewsArticle)"--> B[Create Summaries]
    B --"(summaries, day_summary)" --> C[Conductor]
    C -- Post --> D[Update Website]
    C -- Email Content --> E[Send Newsletter]
    C --> F[Others? Podcast etc]
```