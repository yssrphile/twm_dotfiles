" When started as "evim", evim.vim will already have done these settings, bail
" out.
if v:progname =~? "evim"
  finish
endif

" Get the defaults that most users want.
source $VIMRUNTIME/defaults.vim

if has("vms")
  set nobackup		" do not keep a backup file, use versions instead
else
  set backup		" keep a backup file (restore to previous version)
  if has('persistent_undo')
    set undofile	" keep an undo file (undo changes after closing)
  endif
endif

if &t_Co > 2 || has("gui_running")
  " Switch on highlighting the last used search pattern.
  set hlsearch
endif

" Put these in an autocmd group, so that we can delete them easily.
augroup vimrcEx
  au!

" For all text files set 'textwidth' to 78 characters.
  autocmd FileType text setlocal textwidth=78
augroup END

" Add optional packages.
"
" The matchit plugin makes the % command work better, but it is not backwards
" compatible.
" The ! means the package won't be loaded right away but when plugins are
" loaded during initialization.
if has('syntax') && has('eval')
  packadd! matchit
endif

" #### MANNUALLY ADDED CONFIGS BELOW                                                             #####
" ####################################################################################################
"
" ### STATUSLINE SETTINGS ###
    " {needs updating -- unsure which website showed how to configure these settings}
    "

let g:currentmode={
       \ 'n'  : 'NORMAL ',
       \ 'v'  : 'VISUAL ',
       \ 'V'  : 'V·Line ',
       \ "\<C-V>" : 'V·Block ',
       \ 'i'  : 'INSERT ',
       \ 'R'  : 'R ',
       \ 'Rv' : 'V·Replace ',
       \ 'c'  : 'Command ',
       \}

"
"
"

hi LEDcustCOLOR01 guifg=#e8dfd6 guibg=#ff5879

"
"
"

:set laststatus=2
":set statusline+=%#WildMenu#
:set statusline+=%#ToolbarButton#
:set statusline+=\ %F
":set statusline+=\ %#Search#
:set statusline+=\ %#Conceal#
:set statusline+=\ %y
:set statusline+=\ %m
:set statusline+=\ %r
:set statusline+=%=
:set statusline+=%*
":set statusline+=%#DiffText#
:set statusline+=%#LEDcustCOLOR01#
set statusline+=\ %{toupper(g:currentmode[mode()])}
":set statusline+=%#MatchParen#
":set statusline+=%#StatusLineTerm#
:set statusline+=%#PmenuSel#
:set statusline+=\ [
:set statusline+=\ %4l:%-4L
:set statusline+=\ ]
:set statusline+=\ %7P
:set statusline+=
:set statusline+=

"
" ### COLOR SCHEMES ###
    " [ default ]
""":colorscheme blue
":colorscheme darkblue
""":colorscheme default
":colorscheme delek
":colorscheme desert
":colorscheme elflord
""":colorscheme evening
":colorscheme industry
":colorscheme koehler
""":colorscheme morning
""":colorscheme murphy
":colorscheme pablo
""":colorscheme peachpuff
":colorscheme ron
":colorscheme slate
":colorscheme torte
":colorscheme zellner
"
    " [ non-default ]
    "   > new color schemes downloaded from vimcolors.com
"""""previousdefault""""" :colorscheme miramare
":colorscheme monokai-phoenix
":colorscheme medic_chalk
":colorscheme vice
":colorscheme isotake
":colorscheme focuspoint
":colorscheme vim-framer-syntax
":colorscheme sitruuna
":colorscheme neodark
":colorscheme jellybeans
":colorscheme melange
":colorscheme eldar
":colorscheme wwdc16

"
" ### HIGHTLIGHTING RULES ### 
    " [ enable syntax highlighting ]
:syntax enable
"
    " [ line highlighting ]
"set nu rnu
set nu
set cursorline
hi LineNr ctermfg=2 ctermbg=NONE
"hi CursorLine cterm=NONE ctermbg=DarkGray ctermfg=1
"""hi CursorLineNr ctermbg=NONE ctermfg=1 cterm=NONE
hi CursorLineNr ctermfg=5 cterm=NONE
"
"
    " [ clear search highlighting after search ]
    "   : just hit ENTER key again
nnoremap <CR> :noh<CR><CR>

"
" ### BACKGROUND COLOR FIX ###
    " https://unix.stackexchange.com/questions/516380/terminalkitty-colors-altering-vim-color-scheme
let &t_ut=''

"
" ### TERMINAL MOUSE FIX ###
    " https://stackoverflow.com/questions/7000960/in-vim-why-doesnt-my-mouse-work-past-the-220th-column
if $TERM == 'alacritty'
  set ttymouse=sgr
endif
"
if $TERM == 'kitty'
  set ttymouse=sgr
endif

