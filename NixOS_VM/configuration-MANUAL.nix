# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running ‘nixos-help’).

##### NOTE TO SELF: HOW TO UPDATE THE SYSTEM
##### [1] sudo nix-channel --update
##### [2] sudo nixos-rebuild dry-build
# 
##### [3] [if want to check config] sudo nixos-rebuild test
# 
##### [4] sudo nixos-rebuild switch
# 
##### [5] [only if needed] sudo nix-collect-garbage -d

{ config, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Bootloader.
  boot.loader.grub.enable = true;
  boot.loader.grub.device = "/dev/sda";
  boot.loader.grub.useOSProber = true;

  # Use latest kernel.
  boot.kernelPackages = pkgs.linuxPackages_latest;

  networking.hostName = "nixos"; # Define your hostname.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Enable networking
  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "America/Chicago";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  i18n.extraLocaleSettings = {
    LC_ADDRESS = "en_US.UTF-8";
    LC_IDENTIFICATION = "en_US.UTF-8";
    LC_MEASUREMENT = "en_US.UTF-8";
    LC_MONETARY = "en_US.UTF-8";
    LC_NAME = "en_US.UTF-8";
    LC_NUMERIC = "en_US.UTF-8";
    LC_PAPER = "en_US.UTF-8";
    LC_TELEPHONE = "en_US.UTF-8";
    LC_TIME = "en_US.UTF-8";
  };

  # Enable the X11 windowing system.
  # You can disable this if you're only using the Wayland session.
  services.xserver.enable = true;

  # Enable the KDE Plasma Desktop Environment.
  services.displayManager.sddm.enable = true;
  services.desktopManager.plasma6.enable = true;

  # Configure keymap in X11
  services.xserver.xkb = {
    layout = "us";
    variant = "";
  };

  # Enable CUPS to print documents.
  services.printing.enable = true;

  # Enable sound with pipewire.
  services.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
    # If you want to use JACK applications, uncomment this
    #jack.enable = true;

    # use the example session manager (no others are packaged yet so this is enabled by default,
    # no need to redefine it in your config for now)
    #media-session.enable = true;
  };

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.les_vm = {
    isNormalUser = true;
    description = "Les VM";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [
      kdePackages.kate
    #  thunderbird
    ];
    ### MANUALLY ADDED BELOW #### /// >>>
    shell = pkgs.fish;
    #####
  };

  # Install firefox.
  programs.firefox.enable = true;

  ### MANULALLY ADDED BELOW #### /// >>>
  # Enable fish shell 
  programs.fish.enable = true;
  #####

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
  #  vim # Do not forget to add an editor to edit configuration.nix! The Nano editor is also installed by default.
  #  wget
  ### MANUALLY ADDED BELOW #### /// >>>
  kitty
  fish
  vim
  eza
  bat
  fd
  brave
  oh-my-fish
  git
  #####
  ];

  programs.vim = {
    enable = true;

    extraConfig = ''
      " Get the defaults that most users want.
      source $VIMRUNTIME/defaults.vim

      set termguicolors

      if has("vms")
        set nobackup
      else
        set backup
        if has('persistent_undo')
          set undofile
        endif
      endif

      if &t_Co > 2 || has("gui_running")
        set hlsearch
      endif

      augroup vimrcEx
        autocmd!
        autocmd FileType text setlocal textwidth=78
      augroup END

      if has('syntax') && has('eval')
        packadd! matchit
      endif

      " ===== BASIC =====
      set number
      set cursorline
      syntax enable
      set background=dark
      set laststatus=2

      " ===== BASE COLORS =====
      hi Normal       guifg=#c0c5ce guibg=#2b303b
      hi Cursor       guifg=#2b303b guibg=#eff1f5
      hi Visual       guibg=#4f5b66 guifg=#eff1f5

      " ===== SYNTAX =====
      hi Comment      guifg=#65737e gui=italic
      hi Keyword      guifg=#bf616a gui=bold
      hi String       guifg=#a3be8c
      hi Identifier   guifg=#96b5b4
      hi Function     guifg=#8fa1b3
      hi Type         guifg=#ebcb8b

      " ===== UI =====
      hi LineNr       guifg=#65737e guibg=NONE
      hi CursorLine   guibg=#343d46
      hi CursorLineNr guifg=#eff1f5 gui=bold

      " ===== STATUSLINE (CUSTOM GROUPS) =====
      " {to check for the statusline colors, type :highlight}
      hi MyStatusLeft   guifg=#2b303b guibg=#8fa1b3 gui=bold
      hi MyStatusAccent guifg=#c0c5ce guibg=#4f5b66
      hi MyStatusRight  guifg=#2b303b guibg=#a3be8c gui=bold

      set statusline=
      set statusline+=%#MyStatusLeft#
      set statusline+=\ %F\ 

      set statusline+=%#MyStatusAccent#
      set statusline+=\ %y\ %m\ %r

      set statusline+=%=

      set statusline+=%#MyStatusRight#
      set statusline+=\ [%4l:%-4L]\ 
      set statusline+=\ %7P\ 

      " [ clear search highlighting after search ]
      "   : just hit ENTER key again
      nnoremap <CR> :noh<CR><CR>

      " ### BACKGROUND COLOR FIX ###
      " https://unix.stackexchange.com/questions/516380/terminalkitty-colors-altering-vim-color-scheme
      let &t_ut=''

      " ### TERMINAL MOUSE FIX ###
      " https://stackoverflow.com/questions/7000960/in-vim-why-doesnt-my-mouse-work-past-the-220th-column
      if $TERM == 'alacritty'
        set ttymouse=sgr
      endif

      if $TERM == 'kitty'
        set ttymouse=sgr
      endif
    '';
  };

  ### ***
  ### MANUALLY ADDED BELOW #### /// >>>
  # Set default editor
  environment.variables.EDITOR = "vim";

  # Fonts (recommended for kitty + themes)
  fonts.packages = with pkgs; [
    nerd-fonts.jetbrains-mono
    nerd-fonts.fira-code
    nerd-fonts.roboto-mono
  ];

  # VMware tools (for allowing the guest OS to work seamlessly)
  virtualisation.vmware.guest.enable = true;
  ##### ***

  # Automated Maintenance for Nix Store and Garbage Collection
  nix.settings.auto-optimise-store = true;
  nix.gc = {
    automatic = true;
    dates = "weekly";
    options = "--delete-older-than 3m";
  };

  # Force the sudo lecture warning message every time sudo is used
  security.sudo.extraConfig = ''Defaults lecture=always'';

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # List services that you want to enable:

  # Enable the OpenSSH daemon.
  # services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "26.05"; # Did you read the comment?

}