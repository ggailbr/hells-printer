# Printing Hell's Cube
With the searching I did, I was unable to find a convenient way to download and
print Hell's Cube. This is my attempt at automatically downloading, formatting,
and integrating images from Hell's Cube to MPCFill.

Aiming for an 80% solution

As always, your mileage may vary. I can't promise results and use at your own risk.

**NOTE**: These scripts got close, but there was still a good amount of manual touch-up.
It has only been tested on HC1 and HC6, all others have unknown behavior.

## Planned Process
1. The cards are all linked in the XML downloadable from [Hellfall](https://skeleton.club/hellfall/hellscubes). Using Cockatrice ([Cockatrice](https://github.com/Cockatrice/Cockatrice/wiki/Custom-Cards-&-Sets))
2. Download and tag images based on if they are single or double sided (I am unsure about three sided yet or the foldable one) (In particular:Gristly Bear // Colossal Dradfulmaw needs to meld and is 2 different cards, but one image)
3. Reformat images (split double sided, [upscale](https://github.com/nagadomi/waifu2x) or [upscale](https://github.com/upscayl/upscayl-ncnn) or just use PIL upscale if needed for DPI reqs ...)
4. Add Bleed
5. Create [MPCfill XML](https://github.com/chilli-axe/mpc-autofill/wiki/XML-Schema-Specification#overview) to make ordering easier

## Run Methods:

- Look at the `--help` of `run_all.py`
- Run `copyright_remover.py` to remove copyright notice from cards that it can be removed from
- Run `mpcfill_xml.py` to generate the XML



## Cons
In order to make images the size needed for MPC, we have the option of AI upscaling or general resizing. We did not bother as much with the denoising or 
preserving the text so some fonts may look funky. That being said, I generally liked the output of upscayl the most. To use it
I downloaded the most recent release from [here](https://github.com/upscayl/upscayl-ncnn/releases), then I downloaded the models
for it from [their github](https://github.com/upscayl/custom-models). You can then either copy the files from the release to 
the models repo or you can redirect it using CLI options.

## Naughty List
Cards that have particular exceptions and required manual intervention.

~~- `Sensory Overload` and `Sun Whitan`: These cards seemed to be truncated when they were uploaded to the google content 
storage. As a result, part of the bottom of them gets cutoff and not properly loaded. This manafests as grey space
if truncated images are allowed. To get around this, I found the images in the discord and replaced the download
links in the XML through the `patcher.py`.~~ (Fixed at source)

- `Almighty_Brushwagghc` has atypical edges.
- Any white edges such as `Borrowing_100000_Bears` doesn't play nice with removing corner. Along with odd colors such as `Acquisition_of_Kozilek`

- `Gristly_Bear // Colossal_Dradfulmaw` or really any meld card. 4 sides in 1 image was just too annoying to account for, so they just have a hardcoded cut.
- `Some // Body` For some reason, was split so added exception

- This list is too long to maintain so I'm giving up here...

## Reviewed Cards:
Cards that I looked at and didn't know what to do with

### HC6

- `A Sky Diamond` I am not familiar with what it is spoofing, but I am unsure if it is split or what so I am leaving it as two on one.

## Upscale Comparison
Based on a small search (by smallest original size), the worst cards to upscale were `Goblin Game`, `Throne_of_u_fredfloof`, and `Whale Visions`.

I performed a quick comparison of the various models on `Goblin Game`, but 
did not go through all cards ofc. I tried having AI upscaling, but it would 
weirdly crop cards and I was unsure why so we are sticking with non-AI upscaling
for now.
