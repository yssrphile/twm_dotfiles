
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

" 
"
"
" MANNUALLY ADDED CONFIGS BELOW #####
"
" enable syntax highlighting
:syntax enable
"
" color highlighting
"highlight Normal ctermbg=DarkGray ctermfg=DarkMagenta
"
" vimscript functions from https://shapeshed.com/vim-statuslines/
"function! GitBranch()
"	return system("git rev-parse --abbrev-ref HEAD 2>/dev/null | tr -d '\n'")
"endfunction
"
"function! StatuslineGit()
"	let l:branchname = GitBranch()
"	return strlen(l:branchname) > 0?'  '.l:branchname.' ':''
"endfunction
"
" statusline settings
:set laststatus=2
":set statusline=%#Folded#
":set statusline=%#SpellCap#
:set statusline=%#MatchParen#
":set statusline+=%*
:set statusline+=\ %F
":set statusline+=\ %#SpellCap#
":set statusline+=\ %#WildMenu#
:set statusline+=\ %#Folded#
":set statusline+=%*
:set statusline+=\ %y
":set statusline+=\ %#WildMenu#
":set statusline+=%*
":set statusline+=\ %{StatuslineGit()}
":set statusline+=\ %#SpellBad#
":set statusline+=%*
:set statusline+=\ %m
:set statusline+=\ %r
:set statusline+=%=
:set statusline+=\ [
":set statusline+=\ %{&fileecoding?&fileecoding:&encoding}
":set statusline+=\ ]
:set statusline+=\ %4l:%-4L
:set statusline+=\ ]
:set statusline+=\ %7P
:set statusline+=
:set statusline+=

" new color schemes downloaded from vimcolors.com
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
" ### NON-DEFAULT THEMES BELOW ###
":colorscheme miramare
"
":colorscheme monokai-phoenix
"
":colorscheme medic_chalk
"
":colorscheme vice
"
":colorscheme isotake
"
":colorscheme focuspoint
"
":colorscheme vim-framer-syntax
"
:colorscheme sitruuna
"
"
" line highlighting
"set nu rnu
"set nu
"set cursorline
hi LineNr ctermfg=4
hi CursorLine cterm=NONE ctermbg=DarkGray
hi CursorLineNr ctermbg=NONE ctermfg=5 cterm=NONE
"
"
" clear search highliting after search: just hit ENTER key again
nnoremap <CR> :noh<CR><CR>
