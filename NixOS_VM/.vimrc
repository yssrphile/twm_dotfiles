""" MANUALLY CONFIGURED #### /// >>>
"
set termguicolors
"
"
"
""
"""
""""
"""""
""""
"""
""
"
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
    " {to check for the statusline colors, type :highlight }
    "

" ===== BASIC =====
set number
set cursorline
syntax enable
set background=dark
"set termguicolors
set laststatus=2

" ===== BASE COLORS =====
hi Normal       guifg=#e8dfd6 guibg=#021b21
hi Cursor       guifg=#021b21 guibg=#b5d8f6
hi Visual       guibg=#fffacd guifg=#000000

" ===== SYNTAX =====
hi Comment      guifg=#61778d gui=italic
hi Keyword      guifg=#ff5879 gui=bold
hi String       guifg=#7cbf9e
hi Identifier   guifg=#44b5b1
hi Function     guifg=#9ed9d8
hi Type         guifg=#beb090

" ===== UI =====
hi LineNr       guifg=#61778d guibg=NONE
hi CursorLine   guibg=#032c36
hi CursorLineNr guifg=#b5d8f6 gui=bold

" ===== STATUSLINE (CUSTOM GROUPS) =====
hi MyStatusLeft   guifg=#021b21 guibg=#9ed9d8 gui=bold
hi MyStatusAccent guifg=#e8dfd6 guibg=#61778d
hi MyStatusRight  guifg=#021b21 guibg=#beb090 gui=bold

set statusline=
set statusline+=%#MyStatusLeft#
set statusline+=\ %F\ 

set statusline+=%#MyStatusAccent#
set statusline+=\ %y\ %m\ %r

set statusline+=%=

set statusline+=%#MyStatusRight#
set statusline+=\ [%4l:%-4L]\ 
set statusline+=\ %7P\ 
"
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
