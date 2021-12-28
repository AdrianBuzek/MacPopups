from AppKit import NSAlert, NSInformationalAlertStyle, \
    NSApp, NSCriticalAlertStyle, \
    NSWarningAlertStyle, NSHelpManager, NSObject, NSColor, NSSound, NSURL, NSControl, NSOnState, NSOffState, NSImage,NSMakeSize,\
    NSGraphicsContext,NSImageInterpolationHigh,NSRectFromCGRect,NSBezierPath,NSEvenOddWindingRule,NSZeroPoint,NSMakeRect,\
    NSCompositeSourceOver,NSOpenPanel,NSUserDefaults,NSDistributedNotificationCenter,NSSavePanel,NSArray
from UniformTypeIdentifiers import UTType
from Quartz.CoreGraphics import CGRectMake

def hex_to_rgba(hex, a):
    hex = hex.lstrip("#")
    return (*tuple(int(hex[i:i + 2], 16)/255 for i in (0, 2, 4)), a)

def rounded_corners(image):
    existing_image = image
    existing_size = existing_image.size()
    new_size = NSMakeSize(existing_size.width,existing_size.height)
    composed_image = NSImage.alloc().initWithSize_(new_size)
    composed_image.lockFocus()
    NSGraphicsContext.currentContext().setImageInterpolation_(NSImageInterpolationHigh)
    image_frame = NSRectFromCGRect(CGRectMake(0, 0,existing_size.width,existing_size.height))
    clip_path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(image_frame,existing_size.width/5,existing_size.height/5)
    clip_path.setWindingRule_(NSEvenOddWindingRule)
    clip_path.addClip()
    image.drawAtPoint_fromRect_operation_fraction_(NSZeroPoint,NSMakeRect(0, 0, new_size.width, new_size.height),NSCompositeSourceOver,1)
    composed_image.unlockFocus()
    del clip_path,image,image_frame,new_size,existing_size
    return composed_image

class Color:
    def __new__(cls, **kwargs):
        if kwargs.get("rgba"):
            rgba = kwargs.get("rgba")
        elif kwargs.get("hex"):
            rgba = hex_to_rgba(kwargs.get("hex"), kwargs.get("opacity", 1))
        else:
            raise TypeError("You have to provide one color type. Can be hex or rgba")

        return NSColor.colorWithRed_green_blue_alpha_(*rgba)

class Image:

    def __new__(cls,file_path,size:tuple[int,int],**kwargs):
        img = NSImage.alloc().initByReferencingFile_(file_path)
        #img.setSize_(size)
        if kwargs.get("rounded_corners",True):
           img = rounded_corners(img)
        return img


class CheckBox:
    def __init__(self, checkbox):
        self.__checkbox = checkbox
        self.text = self.__checkbox.title()

    def set_check_box_title(self, title):
        self.__checkbox.setTitle_(title)


class Button:
    def __init__(self, btn):
        self.__btn = btn
        self.title = btn.title()

    def set_color(self, rgb: tuple[float, float, float] = None, **kwargs):
        """
        Change the color of the button to a specific rgb or hex value.
        Note that you are only able to change the color of default buttons. 
        """
        if kwargs.get("hex"):
            color = Color(hex=kwargs.get("hex"))
        else:
            color = Color(rgba=tuple(val/255 for val in rgb)+(1,))
        self.__btn.setBezelColor_(color)

    def set_sound(self, path: str):
        sound = NSSound.alloc()
        sound.initWithContentsOfFile_byReference_(path, 1)
        self.__btn.setSound_(sound)

    def set_default(self, t: bool = False):
        self.__btn.setKeyEquivalent_("\033") if not t else self.__btn.setKeyEquivalent_("\r")


class Alert:

    def __init__(self, informativeText=None, messageText=None, buttons: list[str] = None, check_box: bool = False,
                 **kwargs):
        self.__alert = NSAlert.alloc().init()
        self.buttons = []
        self.check_box = None
        NSApp.activateIgnoringOtherApps_(False)
        if informativeText:
            self.set_informative_text(informativeText)
        if messageText:
            self.set_alert_text(messageText)
        if buttons:
            for button in buttons:
                self.add_button(button)
        self.buttons = [Button(btn) for btn in self.__alert.buttons()]

        defaults = kwargs.get("default", [0])
        if isinstance(defaults, int):
            defaults = [defaults]
        for i,button in enumerate(self.buttons):
            button.set_default(True) if i in defaults else button.set_default(False)
        if check_box:
            text = kwargs.get("box_title")
            self.set_check_box(text)

    def set_icon(self,icon_file,rounded_corners=True):
        icon = Image(icon_file,(100,100),rounded_corners=rounded_corners)
        self.__alert.setIcon_(icon)
    def show(self):
        choice = self.__alert.runModal()

        return choice - 1000, self.__alert.suppressionButton().state()

    def add_button(self, name):
        self.__alert.addButtonWithTitle_(name)

    def set_alert_text(self, text):
        self.__alert.setMessageText_(text)

    def set_informative_text(self, text):
        self.__alert.setInformativeText_(text)

    def set_check_box(self, text=None):
        self.__alert.setShowsSuppressionButton_(True)
        self.check_box = CheckBox(self.__alert.suppressionButton())
        self.check_box.set_check_box_title(text)


class OpenDialog:
    def __init__(self,title="Open",files=True,directories=False,multiple_selection=False,**kwargs):
        self.__dialog = NSOpenPanel.openPanel()
        self.set_title(title)
        self.can_chose_files(files)

        self.can_chose_directories(directories)

        self.multiple_selection(multiple_selection)
        extensions = kwargs.get("extensions")

        if extensions:
            self.file_extensions(extensions)
    def can_chose_files(self,t:bool=True):
        self.__dialog.setCanChooseFiles_(t)

    def can_chose_directories(self,t:bool=False):
        self.__dialog.setCanChooseDirectories_(t)

    def multiple_selection(self,t:bool=False):
        self.__dialog.setAllowsMultipleSelection_(t)

    def file_extensions(self,extensions:list[str]):
        types = [UTType.exportedTypeWithIdentifier_(ext) for ext in extensions]
        self.__dialog.setAllowedContentTypes_(types)
    def set_title(self,title):
        self.__dialog.setTitle_(title)
    def show(self):
        self.__dialog.runModal()
        return list(self.__dialog.URLs())
    
    
class SaveDialog:
    def __init__(self,title="Save",message=None,**kwargs):
        self.__dialog = NSSavePanel.savePanel()
        if kwargs.get("can_create_dirs"):
            self.can_create_directories(kwargs.get("can_create_dirs"))
        self.__dialog.setShowsTagField_(False)
        #self.__dialog.setBackgroundColor_(Color(hex="#000000"))
        self.set_title(title)
        self.set_message(message)

        extensions = kwargs.get("extensions")
        if extensions:
            self.file_extensions(extensions)
    def can_create_directories(self,t):
        self.__dialog.setCanCreateDirectories_(t)

    def file_extensions(self, extensions: list[str]):
        """Error"""
    def set_title(self,title):
        self.__dialog.setTitle_(title)

    def set_message(self,message):
        self.__dialog.setMessage_(message)
    def show(self):
        self.__dialog.runModal()
        return self.__dialog.URL()
