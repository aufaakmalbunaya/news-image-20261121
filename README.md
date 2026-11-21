# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/aufaakmalbunaya/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/aufaakmalbunaya/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Deft Lattice II: a dense newspaper front page summing up Saturday 21 November 2026 in one image. 42 stories, all of which happened or were first reported that day: three hero panels (the overnight missile barrage on Kyiv and the missiles that fell in Poland, Wall Street's Friday rout with the Nasdaq down 5.3%, and Rahul's 93 not out as India fight back in Wellington), twelve illustrated leads (Las Vegas under lights, Voyager 1 a light-day out, Gaza's children, Ebola in Congo, COP31, Bukele's third-term bid, the Houthi strike on a Riyadh tower, Estonia's border closure, Brady's Chelsea talks, India's U17 qualification, the sacked US cyber chief, and California's Nvidia subpoena), a six-number strip, a sketch world map with eight numbered pins, region and field counts that add to 42, 27 more stories in brief, and a date-check footer naming the big 19 November stories deliberately left out (the ICJ Myanmar ruling, the Shenzhen trilateral, the Anthropic debut).

## How it is built

`main.py` draws the whole page (1024x1024 PNG) with the Python standard library only: its own canvas, a 5x7 bitmap font, fourteen flat-vector scene painters, and a PNG encoder written with `zlib` and `struct`. No third-party packages, no network, no clock, no randomness, so the graded run is deterministic and both runs write the same bytes.

## Run it

```sh
python3 main.py          # write entry.png to $MAKEFUN_OUTPUT_DIR
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
