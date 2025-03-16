# Printing Hell's Cube
With the searching I did, I was unable to find a convenient way to download and
print Hell's Cube. This is my attempt at automatically downloading, formatting,
and integrating images from Hell's Cube to MPCFill.

## Planned Process
1. The cards are all linked in the XML downloadable from [Hellfall](https://skeleton.club/hellfall/hellscubes). Using Cockatrice ([Cockatrice](https://github.com/Cockatrice/Cockatrice/wiki/Custom-Cards-&-Sets))
2. Download and tag images based on if they are single or double sided (I am unsure about three sided yet or the foldable one) (In particular:Gristly Bear // Colossal Dradfulmaw needs to meld and is 2 different cards, but one image)
3. Reformat images (split double sided, [upscale](https://github.com/nagadomi/waifu2x) or [upscale](https://github.com/upscayl/upscayl-ncnn) if needed for DPI reqs ...)
4. Use [AutoBleed](https://github.com/Solidsilver/mpc-bleeder) to add the bleed needed for printing.
5. Create [MPCfill XML](https://github.com/chilli-axe/mpc-autofill/wiki/XML-Schema-Specification#overview) to make ordering easier