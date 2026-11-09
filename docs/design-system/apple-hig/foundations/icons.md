# Icons


An effective icon is a graphic asset that expresses a single concept in ways people instantly understand.

![](https://docs-assets.developer.apple.com/published/e71f139e5e50d9d10d91830b0af405c1/foundations-icons-intro%402x.png)

Apps and games use a variety of simple icons to help people understand the items, actions, and modes they can choose. Unlike [App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons), which can use rich visual details like shading, texturing, and highlighting to evoke the app’s personality, an *interface icon* typically uses streamlined shapes and touches of color to communicate a straightforward idea.

You can design interface icons — also called *glyphs* — or you can choose symbols from the SF Symbols app, using them as-is or customizing them to suit your needs. Both interface icons and symbols use black and clear colors to define their shapes; the system can apply other colors to the black areas in each image. For guidance, see [SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols).


### Best practices

**Create a recognizable, highly simplified design.** Too many details can make an interface icon confusing or unreadable. Strive for a simple, universal design that most people will recognize quickly. In general, icons work best when they use familiar visual metaphors that are directly related to the actions they initiate or content they represent.

**Maintain visual consistency across all interface icons in your app.** Whether you use only custom icons or mix custom and system-provided ones, all interface icons in your app need to use a consistent size, level of detail, stroke thickness (or weight), and perspective. Depending on the visual weight of an icon, you may need to adjust its dimensions to ensure that it appears visually consistent with other icons.

![To help achieve visual consistency, adjust individual icon sizes as necessary…](https://docs-assets.developer.apple.com/published/f1cf8ce0ca53b7cb3bce1391a378f6ce/custom-icon-sizes%402x.png)

![…and use the same stroke weight in every icon.](https://docs-assets.developer.apple.com/published/91320cdd7a31574df355383d83eb1ceb/custom-icon-line-weights%402x.png)

**In general, match the weights of interface icons and adjacent text.** Unless you want to emphasize either the icons or the text, using the same weight for both gives your content a consistent appearance and level of emphasis.

**If necessary, add padding to a custom interface icon to achieve optical alignment.** Some icons — especially asymmetric ones — can look unbalanced when you center them geometrically instead of optically. For example, the download icon shown below has more visual weight on the bottom than on the top, which can make it look too low if it’s geometrically centered.

![An asymmetric icon can look off center even though it’s not.](https://docs-assets.developer.apple.com/published/1c13eed753a1ebcfd6d35929738476c7/asymmetric-glyph%402x.png)

In such cases, you can slightly adjust the position of the icon until it’s optically centered. When you create an asset that includes your adjustments as padding around an interface icon (as shown below on the right), you can optically center the icon by geometrically centering the asset.

![Moving the icon a few pixels higher optically centers it; including the pixels in padding simplifies centering.](https://docs-assets.developer.apple.com/published/c31bce31456820badff997c95db264c6/asymmetric-glyph-optically-centered%402x.png)

Adjustments for optical centering are typically very small, but they can have a big impact on your app’s appearance.

![Before optical centering (left) and after optical centering (right).](https://docs-assets.developer.apple.com/published/5d9da37476ee3225a29ce3efbfd86cac/asymmetric-glyph-before-and-after%402x.png)

**Provide a selected-state version of an interface icon only if necessary.** You don’t need to provide selected and unselected appearances for an icon that’s used in standard system components such as toolbars, tab bars, and buttons. The system updates the visual appearance of the selected state automatically.

![In a toolbar, a selected icon receives the app’s accent color.](https://docs-assets.developer.apple.com/published/b5c874fca24c428b421c008b29709986/icons-selection-correct%402x.png)

**Use inclusive images.** Consider how your icons can be understandable and welcoming to everyone. Prefer depicting gender-neutral human figures and avoid images that might be hard to recognize across different cultures or languages. For guidance, see [Inclusion](https://developer.apple.com/design/human-interface-guidelines/inclusion).

**Include text in your design only when it’s essential for conveying meaning.** For example, using a character in an interface icon that represents text formatting can be the most direct way to communicate the concept. If you need to display individual characters in your icon, be sure to localize them. If you need to suggest a passage of text, design an abstract representation of it, and include a flipped version of the icon to use when the context is right-to-left. For guidance, see [Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left).

![Create localized versions of an icon that displays individual characters.](https://docs-assets.developer.apple.com/published/1037fd04c26206ca1b1dee2e34e123af/character-in-glyph%402x.png)
![Create a flipped version of an icon that suggests reading direction.](https://docs-assets.developer.apple.com/published/2edc8ff4ae7af79f32543009ba2f7084/abstract-text-in-glyph%402x.png)

**If you create a custom interface icon, use a vector format like PDF or SVG.** The system automatically scales a vector-based interface icon for high-resolution displays, so you don’t need to provide high-resolution versions of it. In contrast, PNG — used for app icons and other images that include effects like shading, textures, and highlighting — doesn’t support scaling, so you have to supply multiple versions for each PNG-based interface icon. Alternatively, you can create a custom SF Symbol and specify a scale that ensures the symbol’s emphasis matches adjacent text. For guidance, see [SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols).

**Provide alternative text labels for custom interface icons.** Alternative text labels — or accessibility descriptions — aren’t visible, but they let VoiceOver audibly describe what’s onscreen, simplifying navigation for people with visual disabilities. For guidance, see [VoiceOver](https://developer.apple.com/design/human-interface-guidelines/voiceover).

**Avoid using replicas of Apple hardware products.** Hardware designs tend to change frequently and can make your interface icons and other content appear dated. If you must display Apple hardware, use only the images available in [Apple Design Resources](https://developer.apple.com/design/resources/) or the SF Symbols that represent various Apple products.


### Standard icons

For icons to represent common actions in [Menus](https://developer.apple.com/design/human-interface-guidelines/menus), [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars), [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons), and other places in interfaces across Apple platforms, you can use these [SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols).


#### Editing


| Action | Icon | Symbol name |
| --- | --- | --- |
| Cut | ![](https://docs-assets.developer.apple.com/published/16c5fe84ae743e06cf2d388fc64e0cf4/icons-symbols-meaning-cut%402x.png) | `scissors` |
| Copy | ![](https://docs-assets.developer.apple.com/published/a88919c55265efbadeac0df5e16ffd05/icons-symbols-meaning-copy%402x.png) | `document.on.document` |
| Paste | ![](https://docs-assets.developer.apple.com/published/20e32bbb2a3a94eb35d01ddfa9c630e0/icons-symbols-meaning-paste%402x.png) | `document.on.clipboard` |
| Done | ![](https://docs-assets.developer.apple.com/published/833bd3b8ccdf0e2fee0893b3858ddae5/icons-symbols-meaning-done-save%402x.png) | `checkmark ` |
| Save |  |  |
| Cancel | ![](https://docs-assets.developer.apple.com/published/b834206c8d155bc1b0d9d17c206c6da3/icons-symbols-meaning-close-cancel%402x.png) | `xmark` |
| Close |  |  |
| Delete | ![](https://docs-assets.developer.apple.com/published/61f8368d02b05af22d3253a892ced7f3/icons-symbols-meaning-delete%402x.png) | `trash` |
| Undo | ![](https://docs-assets.developer.apple.com/published/e3e973d07e4cfa983c92e37da5b3e104/icons-symbols-meaning-undo%402x.png) | `arrow.uturn.backward` |
| Redo | ![](https://docs-assets.developer.apple.com/published/0f263db97ca2b7c31bbbd3cd5682d071/icons-symbols-meaning-redo%402x.png) | `arrow.uturn.forward` |
| Compose | ![](https://docs-assets.developer.apple.com/published/cfac914468b7fa2f287495f8644f3937/icons-symbols-meaning-compose%402x.png) | `square.and.pencil` |
| Duplicate | ![](https://docs-assets.developer.apple.com/published/96323f746d3c67172648745420a15c27/icons-symbols-meaning-duplicate%402x.png) | `plus.square.on.square` |
| Rename | ![](https://docs-assets.developer.apple.com/published/8d3692b6e29cf0cdcb7885af414b2693/icons-symbols-meaning-rename%402x.png) | `pencil` |
| Move to | ![](https://docs-assets.developer.apple.com/published/77c3e45c395bf2d2225c85979eca53a8/icons-symbols-meaning-move-to-folder%402x.png) | `folder` |
| Folder |  |  |
| Attach | ![](https://docs-assets.developer.apple.com/published/e493eab83f8cc2a6f0aaa2ced386dcff/icons-symbols-meaning-attach%402x.png) | `paperclip` |
| Add | ![](https://docs-assets.developer.apple.com/published/e0a7d36fc7aecfd6e49a4d0c0cb196af/icons-symbols-meaning-add%402x.png) | `plus` |
| More | ![](https://docs-assets.developer.apple.com/published/92e0b17a3881b62008563deb4a2aca40/icons-symbols-meaning-more%402x.png) | `ellipsis` |


#### Selection


| Action | Icon | Symbol name |
| --- | --- | --- |
| Select | ![](https://docs-assets.developer.apple.com/published/7eac493b5a3896062a90328117d43e90/icons-symbols-meaning-select-all%402x.png) | `checkmark.circle` |
| Deselect | ![](https://docs-assets.developer.apple.com/published/b834206c8d155bc1b0d9d17c206c6da3/icons-symbols-meaning-deselect-close%402x.png) | `xmark` |
| Close |  |  |
| Delete | ![](https://docs-assets.developer.apple.com/published/61f8368d02b05af22d3253a892ced7f3/icons-symbols-meaning-delete%402x.png) | `trash` |


#### Text formatting


| Action | Icon | Symbol name |
| --- | --- | --- |
| Superscript | ![](https://docs-assets.developer.apple.com/published/7e5e3d9b1b0eb6f340f531841d6b27f9/icons-symbols-meaning-superscript%402x.png) | `textformat.superscript` |
| Subscript | ![](https://docs-assets.developer.apple.com/published/aac330c124cac37a78e02d6049943e53/icons-symbols-meaning-subscript%402x.png) | `textformat.subscript` |
| Bold | ![](https://docs-assets.developer.apple.com/published/c8695e06d6461e79c145e9b6627f70ac/icons-symbols-meaning-bold%402x.png) | `bold` |
| Italic | ![](https://docs-assets.developer.apple.com/published/9f560283ff88d8d1d4b48f278a831b7b/icons-symbols-meaning-italic%402x.png) | `italic` |
| Underline | ![](https://docs-assets.developer.apple.com/published/3b0d371f10bde381bfa1c9a8999797ec/icons-symbols-meaning-underline%402x.png) | `underline` |
| ​​Align Left | ![](https://docs-assets.developer.apple.com/published/68c0ff42aa0ac813b57b663562198e15/icons-symbols-meaning-align-left%402x.png) | `text.alignleft` |
| Center | ![](https://docs-assets.developer.apple.com/published/a10b48c850a047efd4a72cc2919c30da/icons-symbols-meaning-align-center%402x.png) | `text.aligncenter` |
| Justified | ![](https://docs-assets.developer.apple.com/published/d71f35b4f71149b0b908dd1ff8cfe01e/icons-symbols-meaning-align-justified%402x.png) | `text.justify` |
| Align Right | ![](https://docs-assets.developer.apple.com/published/8af1da29f8f3173510521492642a82be/icons-symbols-meaning-align-right%402x.png) | `text.alignright` |


#### Search


| Action | Icon | Symbol name |
| --- | --- | --- |
| Search | ![](https://docs-assets.developer.apple.com/published/585f5454757731f942979247bf886ecb/icons-symbols-meaning-search%402x.png) | `magnifyingglass` |
| Find | ![](https://docs-assets.developer.apple.com/published/646c6a152822dde685e52a2791ff672f/icons-symbols-meaning-find%402x.png) | `text.page.badge.magnifyingglass` |
| Find and Replace |  |  |
| Find Next |  |  |
| Find Previous |  |  |
| Use Selection for Find |  |  |
| Filter | ![](https://docs-assets.developer.apple.com/published/e0924492d663dac952860673a61f4f96/icons-symbols-meaning-filter%402x.png) | `line.3.horizontal.decrease` |


#### Sharing and exporting


| Action | Icon | Symbol name |
| --- | --- | --- |
| Share | ![](https://docs-assets.developer.apple.com/published/b5fa28be3d82955fc380f44783befd32/icons-symbols-meaning-sharing%402x.png) | `square.and.arrow.up` |
| Export |  |  |
| Print | ![](https://docs-assets.developer.apple.com/published/9de4d23e30e6fd8331215dd6dab12878/icons-symbols-meaning-print%402x.png) | `printer` |


#### Users and accounts


| Action | Icon | Symbol name |
| --- | --- | --- |
| Account | ![](https://docs-assets.developer.apple.com/published/512c86a1c2c99bc09991c89c1e535441/icons-symbols-meaning-account-user%402x.png) | `person.crop.circle` |
| User |  |  |
| Profile |  |  |


#### Ratings


| Action | Icon | Symbol name |
| --- | --- | --- |
| Dislike | ![](https://docs-assets.developer.apple.com/published/189b97655ff655985deec03d0466b898/icons-symbols-meaning-dislike%402x.png) | `hand.thumbsdown` |
| Like | ![](https://docs-assets.developer.apple.com/published/6f38eef523ffbb4f1d6de22a6a022309/icons-symbols-meaning-like%402x.png) | `hand.thumbsup` |


#### Layer ordering


| Action | Icon | Symbol name |
| --- | --- | --- |
| Bring to Front | ![](https://docs-assets.developer.apple.com/published/c5da334738c9baf5ddaa0d6ed9de0af6/icons-symbols-meaning-bring-to-front%402x.png) | `square.3.layers.3d.top.filled` |
| Send to Back | ![](https://docs-assets.developer.apple.com/published/1006037b6fa15950ca7ceb933dbb4805/icons-symbols-meaning-send-to-back%402x.png) | `square.3.layers.3d.bottom.filled` |
| Bring Forward | ![](https://docs-assets.developer.apple.com/published/88b18e0384bca2cd93151169bd507aa3/icons-symbols-meaning-bring-forward%402x.png) | `square.2.layers.3d.top.filled` |
| Send Backward | ![](https://docs-assets.developer.apple.com/published/49eb0ed5381249d763d30d4e515bc57b/icons-symbols-meaning-send-backwards%402x.png) | `square.2.layers.3d.bottom.filled` |


#### Other


| Action | Icon | Symbol name |
| --- | --- | --- |
| Alarm | ![](https://docs-assets.developer.apple.com/published/b777cb6bcc99642b037824c78a7efb0e/icons-symbols-meaning-alarm%402x.png) | `alarm` |
| Archive | ![](https://docs-assets.developer.apple.com/published/50a3b677d72b3d031ea66d10198bfb59/icons-symbols-meaning-archive%402x.png) | `archivebox` |
| Calendar | ![](https://docs-assets.developer.apple.com/published/4b14bf07cf562405caebedb2e200e3dc/icons-symbols-meaning-calendar%402x.png) | `calendar` |


### Platform considerations

*No additional considerations for iOS, iPadOS, tvOS, visionOS, or watchOS.*


#### macOS


##### Document icons

If your macOS app can use a custom document type, you can create a document icon to represent it. Traditionally, a document icon looks like a piece of paper with its top-right corner folded down. This distinctive appearance helps people distinguish documents from apps and other content, even when icon sizes are small.

If you don’t supply a document icon for a file type you support, macOS creates one for you by compositing your app icon and the file’s extension onto the canvas. For example, Preview uses a system-generated document icon to represent JPG files.

![](https://docs-assets.developer.apple.com/published/bfe462604c63811cb542e7c0fc46185e/doc-icon-generated%402x.png)

In some cases, it can make sense to create a set of document icons to represent a range of file types your app handles. For example, Xcode uses custom document icons to help people distinguish projects, AR objects, and Swift code files.

![](https://docs-assets.developer.apple.com/published/8cd56a7291cd6b41fe391958f704c823/doc-icon-custom-1%402x.png)
![](https://docs-assets.developer.apple.com/published/a1449177968f693c1bd68c2b146df7c3/doc-icon-custom-2%402x.png)
![](https://docs-assets.developer.apple.com/published/495bd043bf65349ec96f6728941386f8/doc-icon-custom-3%402x.png)

To create a custom document icon, you can supply any combination of background fill, center image, and text. The system layers, positions, and masks these elements as needed and composites them onto the familiar folded-corner icon shape.

![Background fill](https://docs-assets.developer.apple.com/published/2aed446834a2dc6e8275b6bd7a797ca9/doc-icon-parts-background-fill%402x.png)
![Center image](https://docs-assets.developer.apple.com/published/b59c836903d1b409ab9e21f81762df3e/doc-icon-parts-center-image%402x.png)
![Text](https://docs-assets.developer.apple.com/published/56c5adedc0c08a167a4a03e706924ee6/doc-icon-parts-text%402x.png)

![macOS composites the elements you supply to produce your custom document icon.](https://docs-assets.developer.apple.com/published/d5da9148d27f60891780ab1a9546a111/doc-icon-parts%402x.png)

[Apple Design Resources](https://developer.apple.com/design/resources/#macos-apps) provides a template you can use to create a custom background fill and center image for a document icon. As you use this template, follow the guidelines below.

**Design simple images that clearly communicate the document type.** Whether you use a background fill, a center image, or both, prefer uncomplicated shapes and a reduced palette of distinct colors. Your document icon can display as small as 16x16 px, so you want to create designs that remain recognizable at every size.

**Designing a single, expressive image for the background fill can be a great way to help people understand and recognize a document type.** For example, Xcode and TextEdit both use rich background images that don’t include a center image.

![](https://docs-assets.developer.apple.com/published/8cd56a7291cd6b41fe391958f704c823/doc-icon-custom-1%402x.png)
![](https://docs-assets.developer.apple.com/published/f32709a5ff5742e79fd03a58ae1dd9c6/doc-icon-fill-only%402x.png)

**Consider reducing complexity in the small versions of your document icon.** Icon details that are clear in large versions can look blurry and be hard to recognize in small versions. For example, to ensure that the grid lines in the custom heart document icon remain clear in intermediate sizes, you might use fewer lines and thicken them by aligning them to the reduced pixel grid. In the 16x16 px size, you might remove the lines altogether.

![The 32x32 px icon has fewer grid lines and a thicker EKG line.](https://docs-assets.developer.apple.com/published/1f8bc7946a75363224f373924b557a3a/doc-icon-fewer-details-1%402x.png)
![The 16x16 px @2x icon retains the EKG line but has no grid lines.](https://docs-assets.developer.apple.com/published/e46ac887801d9a16393948c3f2098715/doc-icon-fewer-details-2%402x.png)
![The 16x16 px @1x icon has no EKG line and no grid lines.](https://docs-assets.developer.apple.com/published/fd0d2afcd76a9b25c1217ef2ffb1ad0e/doc-icon-fewer-details-3%402x.png)

**Avoid placing important content in the top-right corner of your background fill.** The system automatically masks your image to fit the document icon shape and draws the white folded corner on top of the fill. Create a set of background images in the sizes listed below.

- 512x512 px @1x, 1024x1024 px @2x
- 256x256 px @1x, 512x512 px @2x
- 128x128 px @1x, 256x256 px @2x
- 32x32 px @1x, 64x64 px @2x
- 16x16 px @1x, 32x32 px @2x

**If a familiar object can convey a document’s type or its connection with your app, consider creating a center image that depicts it.** Design a simple, unambiguous image that’s clear and recognizable at every size. The center image measures half the size of the overall document icon canvas. For example, to create a center image for a 32x32 px document icon, use an image canvas that measures 16x16 px. You can provide center images in the following sizes:

- 256x256 px @1x, 512x512 px @2x
- 128x128 px @1x, 256x256 px @2x
- 32x32 px @1x, 64x64 px @2x
- 16x16 px @1x, 32x32 px @2x

**Define a margin that measures about 10% of the image canvas and keep most of the image within it.** Although parts of the image can extend into this margin for optical alignment, it’s best when the image occupies about 80% of the image canvas. For example, most of the center image in a 256x256 px canvas would fit in an area that measures 205x205 px.

![](https://docs-assets.developer.apple.com/published/7cc19b2ae1e99d26ba69e1351683ede1/doc-icon-parts-margins%402x.png)

**Specify a succinct term if it helps people understand your document type.** By default, the system displays a document’s extension at the bottom edge of the document icon, but if the extension is unfamiliar you can supply a more descriptive term. For example, the document icon for a SceneKit scene file uses the term *scene* instead of the file extension *scn*. The system automatically scales the extension text to fit in the document icon, so be sure to use a term that’s short enough to be legible at small sizes. By default, the system capitalizes every letter in the text.

![](https://docs-assets.developer.apple.com/published/3b4bb7de9edb5870d3a162aae8153163/doc-icon-custom-extension%402x.png)


### Resources


##### Related

[App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)

[SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols)


##### Videos

- [Designing Glyphs](https://developer.apple.com/videos/play/wwdc2017/823)


### Change log


| Date | Changes |
| --- | --- |
| June 9, 2025 | Added a table of SF Symbols that represent common actions. |
| June 21, 2023 | Updated to include guidance for visionOS. |
