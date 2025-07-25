from PIL import Image, ImageDraw, ImageFont


# note: font/background color should be specified with ranges [0-255], not [0-1]
# note: if image width/height not declared, will be set according to rendered text size
class TextImage:
    def __init__(
        self,
        text="Hello, world!",
        fontFileName=None,
        fontSize=24,
        fontColor=None,
        backgroundColor=None,
        transparent=False,
        antialias=True,
        width=None,
        height=None,
        alignHorizontal="LEFT",
        alignVertical="TOP",
    ):
        if backgroundColor is None:
            backgroundColor = [255, 255, 255]
        if fontColor is None:
            fontColor = [0, 0, 0]
        self.text = text
        self.fontFileName = fontFileName
        self.fontSize = fontSize
        self.fontColor = tuple(fontColor)
        self.backgroundColor = tuple(backgroundColor)
        self.transparent = transparent
        self.antialias = antialias  # Note: Pillow handles antialiasing automatically
        self.width = width
        self.height = height
        self.alignHorizontal = alignHorizontal
        self.alignVertical = alignVertical

        # Load font
        if fontFileName is None:
            # Try to load a default system font
            try:
                self.font = ImageFont.truetype("arial.ttf", fontSize)
            except OSError:
                # If arial is not available, use default
                self.font = ImageFont.load_default()
        else:
            try:
                self.font = ImageFont.truetype(fontFileName, fontSize)
            except OSError:
                print(f"Could not load font {fontFileName}, using default")
                self.font = ImageFont.load_default()

        self.renderImage()

    # can call to recalculate surface if text has changed
    def renderImage(self):
        # Create a temporary image to measure text size
        temp_img = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)

        # Determine text size
        textbbox = temp_draw.textbbox((0, 0), self.text, font=self.font)
        textWidth = textbbox[2] - textbbox[0]
        textHeight = textbbox[3] - textbbox[1]

        # if image dimensions are not specified, use font surface size as default
        if self.width is None:
            self.width = textWidth
        if self.height is None:
            self.height = textHeight

        # Create image with transparency channel
        if self.transparent:
            self.surface = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        else:
            self.surface = Image.new("RGBA", (self.width, self.height), self.backgroundColor)

        draw = ImageDraw.Draw(self.surface)

        # Calculate position based on alignment
        if self.alignHorizontal == "LEFT":
            alignX = 0
        elif self.alignHorizontal == "CENTER":
            alignX = (self.width - textWidth) // 2
        elif self.alignHorizontal == "RIGHT":
            alignX = self.width - textWidth

        if self.alignVertical == "TOP":
            alignY = 0
        elif self.alignVertical == "MIDDLE":
            alignY = (self.height - textHeight) // 2
        elif self.alignVertical == "BOTTOM":
            alignY = self.height - textHeight

        # Draw text
        draw.text((alignX, alignY), self.text, font=self.font, fill=self.fontColor)
