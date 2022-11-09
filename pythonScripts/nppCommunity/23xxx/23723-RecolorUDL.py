# encoding=utf-8
"""in response to https://community.notepad-plus-plus.org/topic/23723/

My idea is to look at the HiddenLexers, especially the Colorize method,
and try to see if I can live-edit the UDL colors
"""
from Npp import editor,notepad,console
from ctypes import windll, WINFUNCTYPE, addressof, create_unicode_buffer
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, HMODULE, LPCWSTR, LPCSTR, LPVOID
from time import sleep
from math import sqrt, floor

windll.user32.SendMessageW.argtypes = [HWND, UINT, WPARAM, LPARAM]
windll.user32.SendMessageW.restype  = LPARAM

class ThisIsTheClass(object):
    _lexer_name = b"Markdown (preinstalled)"
    _lexer_unic = create_unicode_buffer(_lexer_name)
    notepad_hwnd = windll.user32.FindWindowW(u'Notepad++', None)
    editor1_hwnd = windll.user32.FindWindowExW(notepad_hwnd, None, u"Scintilla", None)
    editor2_hwnd = windll.user32.FindWindowExW(notepad_hwnd, editor1_hwnd, u"Scintilla", None)

    # https://github.com/notepad-plus-plus/notepad-plus-plus/blob/b502266e8d70a5dc9069e13d2d18ef071aea5578/lexilla/include/SciLexer.h#L209-L233
    SCE_USER_STYLE_DEFAULT              = 0
    SCE_USER_STYLE_COMMENT              = 1
    SCE_USER_STYLE_COMMENTLINE          = 2
    SCE_USER_STYLE_NUMBER               = 3
    SCE_USER_STYLE_KEYWORD1             = 4
    SCE_USER_STYLE_KEYWORD2             = 5
    SCE_USER_STYLE_KEYWORD3             = 6
    SCE_USER_STYLE_KEYWORD4             = 7
    SCE_USER_STYLE_KEYWORD5             = 8
    SCE_USER_STYLE_KEYWORD6             = 9
    SCE_USER_STYLE_KEYWORD7             = 10
    SCE_USER_STYLE_KEYWORD8             = 11
    SCE_USER_STYLE_OPERATOR             = 12
    SCE_USER_STYLE_FOLDER_IN_CODE1      = 13
    SCE_USER_STYLE_FOLDER_IN_CODE2      = 14
    SCE_USER_STYLE_FOLDER_IN_COMMENT    = 15
    SCE_USER_STYLE_DELIMITER1           = 16
    SCE_USER_STYLE_DELIMITER2           = 17
    SCE_USER_STYLE_DELIMITER3           = 18
    SCE_USER_STYLE_DELIMITER4           = 19
    SCE_USER_STYLE_DELIMITER5           = 20
    SCE_USER_STYLE_DELIMITER6           = 21
    SCE_USER_STYLE_DELIMITER7           = 22
    SCE_USER_STYLE_DELIMITER8           = 23
    SCE_USER_STYLE_IDENTIFIER           = 24

    def __init__(self):

        console.show()
        console.clear()
        console.write("NPPv{}\ttxt:'{}' uni:'{}'\n".format(self.nppver(), self._lexer_name, self._lexer_unic))
        #if self.nppver() < 8.410:
        #    raise ValueError("NPP v{} is too old; upgrade to at least NPP v8.4.1".format(self.nppver()))
        #
        #self.ilexer_ptr = windll.user32.SendMessageW(self.notepad_hwnd, self.NPPM_CREATELEXER, 0, addressof(self._lexer_unic))


    def nppver(self):
        self.NPPM_GETNPPVERSION = 1024 + 1000 + 50
        nppv = windll.user32.SendMessageW(self.notepad_hwnd, self.NPPM_GETNPPVERSION, 1, 0 )
        # for v8.4.1 and newer, this will pad it as 8<<16 + 410 for easy comparison
        # v8.4 will be under old scheme of 8<<16 + 4, v8.3.3 is 8<<16 + 33
        ver = nppv >> 16    # major version
        mnr = nppv & 0xFFFF # minor version
        if (ver <= 8) and (mnr < 10):
            ver += mnr/10.
        elif (ver <= 8) and (mnr < 100):
            ver += mnr/100.
        elif (ver>8) or (mnr>99):
            ver += mnr/1000.

        return ver

    def example(self):
        notepad.new()

        notepad.runMenuCommand('Language', self._lexer_name)
        editor.setText("""# Hello World

This is it

- Bullet 1
- Bullet 2

1. Ordered
2. List

_italic_
**bold**

5 + 6
"""
        )
        editor.setSavePoint() # fake save point
        editor.gotoPos(0xFFFF)
        #for s in range(0,25):
        #    fg, bg = editor.styleGetFore(s), editor.styleGetBack(s)
        #    console.write("style#{}\tfg = {}:{}, bg = {}:{}\n".format(int(s),fg,self.rgbLum(fg),bg,self.rgbLum(bg)))
        console.write("isDarkMode? {}\n".format(self.isDarkMode()))

        self.colorize()
        sleep(5)
        notepad.close()
        return

    def colorize(self):
        default_fg = editor.styleGetFore(0)
        default_bg = editor.styleGetBack(0)
        console.write("default_fg = {}\ndefault_bg = {}\n".format(default_fg, default_bg))
        sleep(1)

        ###OLD### # if the UDL has a dark background and it's in Light Mode,
        ###OLD### #   or UDL has a light background and it's in Dark Mode,
        ###OLD### #   adjust the colors
        ###OLD### #
        ###OLD### if (L<0.5 and not(self.isDarkMode())) or (L>0.5 and self.isDarkMode()):
        # now assumes that you have a light mode UDL and want to invert it only when you are in Dark Mode; just use a not after the if to get it to invert a dark UDL in a LightMode NPP
        if self.isDarkMode():
            console.write("COLORIZING...\n")
            for sty in range(0,25):   # UDL has style numbers 0..24
                # only invert the foreground if it wasn't transparent/inherited or otherwise the same as the default fg
                fg = editor.styleGetFore(sty)
                if fg != default_fg:
                    hsl = self.rgb2hsl(fg)
                    hsl2 = (hsl[0], hsl[1], 1-hsl[2])   # invert the luminosity
                    rgb = self.hsl2rgb(hsl2)
                    console.write("DEBUG: FG#{}\t{} = HSL:{} => HSL2:{} = rgb:{}\n".format(sty, fg, hsl, hsl2, rgb))
                    editor.styleSetFore(sty,tuple(rgb))

                # TODO: the HSL->RGB doesn't look right; need to check out why (0,0,128)->(4,0,.25) but (4,0,.75)->(191,191,191)
                #       and (255, 128, 0) = HSL:(0, 1.0, 0.5) => HSL2:(0, 1.0, 0.5) = rgb:(255, 0, 0)

                # only invert the background if it wasn't transparent/inherited or otherwise the same as the default bg
                bg = editor.styleGetBack(sty)
                if bg != default_bg:
                    hsl = self.rgb2hsl(bg)
                    hsl2 = (hsl[0], hsl[1], 1-hsl[2])   # invert the luminosity
                    rgb = self.hsl2rgb(hsl2)
                    console.write("DEBUG: BG#{}\t{} = HSL:{} => HSL2:{} = rgb:{}\n".format(sty, bg, hsl, hsl2, rgb))
                    editor.styleSetBack(sty,tuple(rgb))
        else:
            console.write("NO INVERSION...\n")

        notepad.activateFile(notepad.getCurrentFilename()) # refresh UI

        return

    def isDarkMode(self):
        return 1L == windll.user32.SendMessageW(ThisIsTheClass.notepad_hwnd, 1024 + 1000 + 107, 0, 0)

    def rgbLum(self, rgb):
        return 0.5*(min(rgb) + max(rgb))/255
        #return int(floor(sqrt(rgb[0]**2 + rgb[1]**2 + rgb[2]**2)/sqrt(3)))

    def rgb2hsl(self, rgb):
        """ rgb to fractional hsl tuple: "h" is H/60deg or H/40hue, so a number from 0 to 6, s and v are from 0 to 1, inclusive """
        c = (max(rgb) - min(rgb))
        l = 0.5*(max(rgb) + min(rgb))/255
        if c==0:
            h = 0
        elif max(rgb) == rgb[0]:
            h = (rgb[1]-rgb[2])/c % 6
        elif max(rgb) == rgb[1]:
            h = (rgb[2]-rgb[0])/c + 2
        elif max(rgb) == rgb[2]:
            h = (rgb[0]-rgb[1])/c + 4
        else:
            raise ValueError("rgb2hsl(RGB={}) => c={}, max={}: max not found?!".format(rgb, c, max(rgb)))

        s = 0 if (l==0.0 or l==1.0) else c/255 / (1 - abs(2*l-1))
        #console.write("\tRGB:{} => HSL:({:d},{:06.2%},{:06.2%})\n".format(rgb, h, s, l))
        return (h,s,l)

    def hsl2rgb(self, hsl):
        """ fractional hsl back to rgb tuple """
        h,s,l = hsl
        c = (1-abs(2*l-1)) * s * 255
        x = c*(1-abs(h%2 - 1))
        m = (l*255 - c/2)
        if h<1:
            rgb = ([int(floor(q+m)) for q in [c,x,0]])
        elif h<2:
            rgb = ([int(floor(q+m)) for q in [x,c,0]])
        elif h<3:
            rgb = ([int(floor(q+m)) for q in [0,c,x]])
        elif h<4:
            rgb = ([int(floor(q+m)) for q in [0,x,c]])
        elif h<5:
            rgb = ([int(floor(q+m)) for q in [x,0,c]])
        else:
            rgb = ([int(floor(q+m)) for q in [c,0,x]])

        return tuple(rgb)



ThisIsTheClass().example()


"""
144,224,224 => 120/135/173
0,80,80     => 120/240/38
18,67,67    => 120/135/40

HSL to RGB:
    M,m=Max,Min(R,G,B)  in the range [0..1]
    C = M-m
    H = { any               | C==0
          (G-B)/C mod 6     | M==R
          (B-R)/C + 2       | M==G
          (R-G)/C + 4       | M==B
        } * 40hue                       -- wikipedia uses 60deg, windows uses H from 0:240, so I will call the units "hue" instead of "deg"
    L = 0.5*(M+m)       [0..1]


M,m=224,144
C=80
H=[(224-144)/80 + 2]*40hue = 120


Claims HSL->RGB:
120/135/173
C = (1-|2*L/240-1|) * S = (1-|2*173/240-1|)*135/240
    = (1-0.4416)*0.5625 = 0.314
H' = H/60 = 120/60 = 2
X = C*(1-|H' mod 2 - 1|) = 0.314*(1-|-1|) = 0
RGB'= {         | for H':
        (C,X,0) | 0 .. 1
        (X,C,0) | 1 .. 2
        (0,C,X) | 2 .. 3
        (0,X,C) | 3 .. 4
        (X,0,C) | 4 .. 5
        (C,0,X) | 5 .. 6
      }
m = L - C/2
RGB = RGB' + m

H' = 2 -> (0,C,0) = (0,.314,0)*255 = (0,80,0)
m = 173/240 - .314/2 = 0.563 => 144
    144,224,144


Windows uses H from 0..240 as well.  So it's 40hue instead of 60hue each


C = max:224 - min:144 = range:80
H = (B-R)/C + 2 = (224-144)/80 + 2 = 3 => 120hue
L = 0.5*(max+min) => 0.5*(144+224)/255 = 184/255 = 0.72157 => 173.17

S = 0 if L-1 or 0 (no) or C/(1-|2L-1|)
    (80/255) / (1-|2*.72157-1|) = 0.314 / ( 1-.44314) = .564
    .564*240 = 135

"""
