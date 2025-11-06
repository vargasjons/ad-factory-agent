# Fonts Directory

This directory contains custom fonts for subtitle generation in the UGC Agent.

**Location:** `ugc_agent/tools/utils/fonts/`

## Supported Fonts

The `AddSubtitles` tool supports the following fonts:
- **Montserrat** (default)
- **Gibson**
- **Barlow Condensed**
- **Komika Axis**
- **Futura**
- **Arial** (system fallback)

## How to Add Fonts

1. Download the font files (.ttf format) for the fonts you want to use
2. Place them in this `ugc_agent/tools/utils/fonts/` directory

### Recommended Font Files

For best results, use **Bold** or **SemiBold** weights:

- `Montserrat-Bold.ttf` or `Montserrat-SemiBold.ttf`
- `Gibson-Bold.ttf` or `Gibson-SemiBold.ttf`
- `BarlowCondensed-Bold.ttf` or `BarlowCondensed-SemiBold.ttf`
- `KomikaAxis.ttf` or `KomikaAxis-Bold.ttf`
- `Futura-Bold.ttf` or `Futura-Medium.ttf`

## Where to Download Fonts

### Free Fonts (Google Fonts)
- **Montserrat**: https://fonts.google.com/specimen/Montserrat
- **Barlow Condensed**: https://fonts.google.com/specimen/Barlow+Condensed

### Commercial Fonts
- **Gibson**: Commercial font (requires purchase)
- **Komika Axis**: Available from font marketplaces
- **Futura**: Commercial font (requires purchase)

## Font Loading Priority

The tool will try to load fonts in this order:
1. `ugc_agent/tools/utils/fonts/` directory
2. Windows system fonts (`C:/Windows/Fonts/`)
3. Current directory
4. Fallback to Arial if custom font not found

## Usage Example

```python
from ugc_agent.tools.AddSubtitles import AddSubtitles

tool = AddSubtitles(
    video_name="my_video",
    font="Montserrat",  # Choose from supported fonts
    font_size=60,
    position="bottom",
    highlight_color="yellow"
)
result = tool.run()
```

