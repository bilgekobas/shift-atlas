# Assets

This folder contains static assets used by the atlas.

Recommended structure:

```text
assets/
├── cases/
│   ├── antakya-courtyard-house/
│   │   ├── hero.jpg
│   │   ├── plan.jpg
│   │   ├── section.jpg
│   │   └── source.txt
│   └── kepenek/
│       ├── hero.jpg
│       └── source.txt
├── icons/
└── maps/
```

## Case image rule

Do not rely on automatic image fallback for atlas cases.

Each case should explicitly declare local images in the HTML or data file, for example:

```js
imgs: [
  { src: "assets/cases/kepenek/hero.jpg", label: "Photograph" },
  { src: "assets/cases/kepenek/detail.jpg", label: "Detail" }
]
```

## Image credit rule

Each case image folder should contain a `source.txt` file with:

- image filename
- author / photographer / source
- URL or publication source
- license status
- date accessed, if web-based
- whether the image can be redistributed on GitHub Pages
