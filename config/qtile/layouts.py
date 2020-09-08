### MOSTLY BORROWED/INSPIRED BY GITHUB QTILE EXAMPLES: LIGHTSPEEDLIFE
### https://github.com/qtile/qtile-examples/blob/master/lightspeedlife
#
#
#

from libqtile import layout


def init_layouts(layout_defaults):
    return [
        layout.Max(**layout_defaults),
        layout.Stack(**layout_defaults, num_stacks=2),
        # Try more layouts by unleashing below layouts.
        # layout.Bsp(**layout_defaults),
        # layout.Columns(**layout_defaults),
        # layout.Matrix(**layout_defaults),
        layout.MonadTall(**layout_defaults),##
        # layout.MonadWide(**layout_defaults),
        layout.RatioTile(**layout_defaults),##
        # layout.Tile(**layout_defaults),
        layout.TreeTab(**layout_defaults),##
        # layout.VerticalTile(**layout_defaults),
        ### layout.Zoomy(**layout_defaults),##
    ]


