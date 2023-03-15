" CONFIG adapted from a vimrc file.

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

" #### MANNUALLY ADDED CONFIGS BELOW                                                             #####
" ####################################################################################################
"
" ### STATUSLINE SETTINGS ###
"   " [ website ]
"   "   > https://shapeshed.com/vim-statuslines/
"   "   > use :highlight to see what options there are
:set laststatus=2
:set statusline+=%#DiffText#
:set statusline+=\ %F
":set statusline+=%*
":set statusline+=\ %#FoldColumn#
":set statusline+=\ %#QuickFixLine#
:set statusline+=\ %#TabLineSel#
:set statusline+=\ %y
:set statusline+=\ %m
:set statusline+=\ %r
":set statusline+=%*
":set statusline+=%#SignColumn#
:set statusline+=%=
:set statusline+=\ [
:set statusline+=\ %4l:%-4L
:set statusline+=\ ]
:set statusline+=\ %7P
:set statusline+=
:set statusline+=

" ### COLOR SCHEMES ###
    " [ default ]
":colorscheme darkblue
":colorscheme delek
":colorscheme desert
":colorscheme elflord
":colorscheme industry
":colorscheme koehler
":colorscheme pablo
":colorscheme ron
":colorscheme slate
":colorscheme torte
":colorscheme zellner
    " [ non-default ]
    "   > new color schemes downloaded from vimcolors.com
":colorscheme miramare
":colorscheme monokai-phoenix
":colorscheme medic_chalk
":colorscheme isotake
":colorscheme focuspoint
":colorscheme vim-framer-syntax
":colorscheme sitruuna
":colorscheme neodark
:colorscheme jellybeans
":colorscheme melange
":colorscheme eldar
":colorscheme wwdc16

" ### HIGHTLIGHTING RULES ### 
    " [ enable syntax highlighting ]
:syntax enable
    " [ line highlighting ]
set nu
set cursorline
hi LineNr ctermfg=2 ctermbg=NONE
hi CursorLineNr ctermfg=5 cterm=NONE
    " [ clear search highlighting after search : just hit ENTER key again ]
nnoremap <CR> :noh<CR><CR>

" ### RESTORE CURSOR POSITON ###
"   " [ custom code for nvim ]
"   "   : https://www.reddit.com/r/neovim/comments/632wh4/neovim_does_not_save_last_cursor_position/
autocmd BufReadPost * if @% !~# '\.git[\/\\]COMMIT_EDITMSG$' && line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g`\"" | endif 

" ### TERMINAL MOUSE FIX ###
    " https://stackoverflow.com/questions/65350712/what-is-set-mouse-a-for-in-nvim
set mouse=a
