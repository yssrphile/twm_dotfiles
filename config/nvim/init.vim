
" An example for a vimrc file.
"
" Maintainer:	Bram Moolenaar <Bram@vim.org>
" Last change:	2019 Dec 17
"
" To use it, copy it to
"	       for Unix:  ~/.vimrc
"	      for Amiga:  s:.vimrc
"	 for MS-Windows:  $VIM\_vimrc
"	      for Haiku:  ~/config/settings/vim/vimrc
"	    for OpenVMS:  sys$login:.vimrc

" When started as "evim", evim.vim will already have done these settings, bail
" out.
if v:progname =~? "evim"
  finish
endif

" Get the defaults that most users want.
"""source $VIMRUNTIME/defaults.vim

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

" 
"
"
" #### MANNUALLY ADDED CONFIGS BELOW                                                             #####
" ####################################################################################################
"
" ### VIMSCRIPT FUNCTIONS ###
    " git function from https://vi.stackexchange.com/questions/26708/how-to-get-vim-to-show-git-status-in-the-statusline
"augroup gitstatusline
"    au!
"
"    autocmd BufEnter,FocusGained,BufWritePost *
"        \ let b:git_clean = system(printf("cd %s && git status --porcelain 2>/dev/null", expand('%:p:h:S'))) is# ''
"augroup end
"
"function! GitLineInfo2() abort
"    return get(b:, "git_clean", "") ? "[clean]" : "[changed]"
"endfunction
"
"function! GitLineInfo1() abort
"    return substitute(system("git status -s"), "\n", " ", "g")
"endfunction

"
"
" ### STATUSLINE SETTINGS ###
    " {needs updating -- unsure which website showed how to configure these settings}
    "
:set laststatus=2
:set statusline=%#WildMenu#
":set statusline+=%*
:set statusline+=\ %F
:set statusline+=\ %#Search#
":set statusline+=%*
:set statusline+=\ %y
":set statusline+=%*
:set statusline+=\ %m
:set statusline+=\ %r
:set statusline+=%=
:set statusline+=\ [
:set statusline+=\ %4l:%-4L
:set statusline+=\ ]
:set statusline+=\ %7P
:set statusline+=
:set statusline+=

"
"
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
"
    " [ non-default ]
    "   > new color schemes downloaded from vimcolors.com
":colorscheme miramare
":colorscheme monokai-phoenix
":colorscheme medic_chalk
":colorscheme isotake
:colorscheme focuspoint
":colorscheme vim-framer-syntax
":colorscheme sitruuna
":colorscheme neodark
":colorscheme jellybeans
":colorscheme melange
":colorscheme eldar
":colorscheme wwdc16

"
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
hi CursorLineNr ctermfg=5 cterm=NONE
"
"
    " [ clear search highlighting after search ]
    "   : just hit ENTER key again
nnoremap <CR> :noh<CR><CR>

"
"
" ### RESTORE CURSOR POSITON ###
"   " [ custom code for nvim ]
"   "   : https://www.reddit.com/r/neovim/comments/632wh4/neovim_does_not_save_last_cursor_position/
autocmd BufReadPost * if @% !~# '\.git[\/\\]COMMIT_EDITMSG$' && line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g`\"" | endif

