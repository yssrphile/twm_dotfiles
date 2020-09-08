# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List  # noqa: F401

from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group, Key, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

mod = "mod4"
terminal = guess_terminal()

keys = [
    # Switch between windows in current stack pane
    ### swapped the default keybinds below, to match vim
    Key([mod], "j", lazy.layout.down(),
        desc="Move focus down in stack pane"),
    Key([mod], "k", lazy.layout.up(),
        desc="Move focus up in stack pane"),
    ### added the four keybindss below b/c I like arrows too
    Key([mod], "Down", lazy.layout.down(),
        desc="Move focus down in stack pane"),
    Key([mod], "Up", lazy.layout.up(),
        desc="Move focus up in stack pane"),
    Key([mod], "Left", lazy.layout.left(),
        desc="Move focus left in stack pane"),
    Key([mod], "Right", lazy.layout.right(),
        desc="Move focus up in stack pane"),

    # Move windows up or down in current stack
    ### swapped the default keybinds below, to match vim
    Key([mod, "control"], "j", lazy.layout.shuffle_down(),
        desc="Move window down in current stack "),
    Key([mod, "control"], "k", lazy.layout.shuffle_up(),
        desc="Move window up in current stack "),

    # Switch window focus to other pane(s) of stack
    Key([mod], "space", lazy.layout.next(),
        desc="Switch window focus to other pane(s) of stack"),

    # Swap panes of split stack
    Key([mod, "shift"], "space", lazy.layout.rotate(),
        desc="Swap panes of split stack"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "Tab", lazy.prev_layout(), desc="Toggle backward between layouts"),
    ## changed default "w" below to "q"
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control"], "r", lazy.restart(), desc="Restart qtile"),
    ## changed default "q" below to "0"
    Key([mod, "control"], "0", lazy.shutdown(), desc="Shutdown qtile"),
    Key([mod], "r", lazy.spawncmd(),
        desc="Spawn a command using a prompt widget"),

    ### MY OWN MISC. CREATED KEYBINDINGS ###
    Key([mod], "f", lazy.spawn("firefox"), desc="Launch Firefox web browser"),
    Key([mod], "z", lazy.spawn("dmenu_run -h 16"), desc="Run dmenu"),
    # >> look in ~/dmenu/config.h for configurable options/flags and to change color scheme
]

groups = [Group(i) for i in "12345678"]
###groups = [Group(i) for i in "asdfuiop"] ## this is the default

for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key([mod], i.name, lazy.group[i.name].toscreen(),
            desc="Switch to group {}".format(i.name)),

        # mod1 + shift + letter of group = switch to & move focused window to group
        ###Key([mod, "shift"], i.name, lazy.window.togroup(i.name, switch_group=True),
        ###    desc="Switch to & move focused window to group {}".format(i.name)),
        # Or, use below if you prefer not to switch to that group.
        # # mod1 + shift + letter of group = move focused window to group
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name), ### uncommented
             desc="move focused window to group {}".format(i.name)), ### uncommented
    ])

layouts = [
    layout.MonadTall(),##
    layout.RatioTile(),##
    layout.TreeTab(),##
    layout.Max(),
    ###layout.Stack(num_stacks=2),
    # Try more layouts by unleashing below layouts.
    # layout.Bsp(),
    # layout.Columns(),
    # layout.Matrix(),
    # layout.MonadWide(),
    # layout.Tile(),
    # layout.VerticalTile(),
    ###layout.Zoomy(),##
]

widget_defaults = dict(
    font='sans',
    fontsize=14,
    padding=3,
)
extension_defaults = widget_defaults.copy()

### THE BAR SETTINGS BELOW HAVE BEEN EDITED/CUSTOMIZED ###

## MY DEFINED BAR COLORS ##
themeColor = [
        "021b21", # panel bg
        "e8dfd6", # panel fg (text)
        "032c36", # 00: current screen tab bg
        "065f73", # 08: 
        "c2454e", # 01: 
        "ef5847", # 09: 
        "7cbf9e", # 02: 
        "a2d9b1", # 10: 
        "8a7a63", # 03: 
        "beb090", # 11: 
        "2e3340", # 04: 
        "61778d", # 12: 
        "ff5879", # 05: 
        "ff99a1", # 13: 
        "44b5b1", # 06: 
        "9ed9d8", # 14: 
        "f2f1b9", # 07: 
        "f6f6c9", # 15: 
        ]

themeColors = {
        "bg":themeColor[0], # 
        "fg":themeColor[1], #
        "00":themeColor[2], #
        "08":themeColor[3], #
        "01":themeColor[4], #
        "09":themeColor[5], #
        "02":themeColor[6], #
        "10":themeColor[7], #
        "03":themeColor[8], #
        "11":themeColor[9], #
        "04":themeColor[10], #
        "12":themeColor[11], #
        "05":themeColor[12], #
        "13":themeColor[13], #
        "06":themeColor[14], #
        "14":themeColor[15], #
        "07":themeColor[16], #
        "15":themeColor[17], #
        }

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(foreground=themeColors["09"]),
                widget.GroupBox(active=themeColors["07"], inactive=themeColors["04"], highlight_method="block", block_highlight_text_color=themeColors["13"]),
                widget.Prompt(),
                widget.WindowName(foreground=themeColors["06"]),
                widget.Chord(
                    chords_colors={
                        'launch': (themeColors["04"], themeColors["12"]),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                widget.TextBox("default config", name="default", foreground=themeColors["03"]),
                widget.TextBox("Press &lt;M-r&gt; to spawn", foreground=themeColors["02"]),
                widget.Systray(),
                #widget.CPU(),
                widget.Clock(format='%Y-%m-%d %a %I:%M %p', foreground=themeColors["12"]),
                widget.QuickExit(foreground=themeColors["09"]),
            ],
            30,
            background=themeColors["bg"],
            margin=2,
            opacity=0.98,
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and will be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    {'wmclass': 'confirm'},
    {'wmclass': 'dialog'},
    {'wmclass': 'download'},
    {'wmclass': 'error'},
    {'wmclass': 'file_progress'},
    {'wmclass': 'notification'},
    {'wmclass': 'splash'},
    {'wmclass': 'toolbar'},
    {'wmclass': 'confirmreset'},  # gitk
    {'wmclass': 'makebranch'},  # gitk
    {'wmclass': 'maketag'},  # gitk
    {'wname': 'branchdialog'},  # gitk
    {'wname': 'pinentry'},  # GPG key password entry
    {'wmclass': 'ssh-askpass'},  # ssh-askpass
])
auto_fullscreen = True
focus_on_window_activation = "smart"

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
