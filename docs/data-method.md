# Data & Method

## Climate data

The atlas prototype uses monthly climate summaries derived from climate data streams such as ERA5/Open-Meteo, depending on the current implementation of the HTML file.

Typical variables include:

- monthly maximum temperature
- monthly minimum temperature
- precipitation
- relative or absolute humidity
- solar radiation

## Future climate

Future climate values are currently represented through projected scenario shifts, with SSP5-8.5 used in the current prototype.

## Climate analogues

The atlas uses climate analogue matching to compare a case location's projected future climate with present-day candidate-city climates.

The analogue should be interpreted as an approximate communication device, not as a precise prediction.

Recommended display:

```text
Future climate analogue: City, Country — 83/100 similarity
```

Detailed methodological metrics can remain in the method documentation rather than inside every card.

## Case data

Case entries are editorially structured using:

```text
Condition → Mechanism → Strategy Family → Regional Variant / Case → Element
```

## Limitations

- Climate data may be unavailable or incomplete for some locations.
- Analogue matching depends on candidate-city coverage.
- Student sourcebooks may require editorial supplementation.
- Images must be verified before public use.
