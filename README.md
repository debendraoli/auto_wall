# AUTO WALL

Most Advance Cross Platform Desktop Screen Wall Manipulation Program written in python.

Extremely lightweight without the need of any third party packages.

![https://imgur.com/GTg5loN.png](https://imgur.com/GTg5loNl.png)
## 1. Installation

Python 3.5 or above is required to run to run the program.

1. Clone or download the zip archive from github repo.
2. Extract or cd into the project folder and run `python setup.py`

***# TODO HERE***

```
[debendra@debendra-pc ~]$ git clone https://
[debendra@debendra-pc ~]$ cd auto_wall
[debendra@debendra-pc ~/auto_wall]$ python setup.py
```

## 2. Features

1. Interactive command line interface.
2. Random image selection from local directory.
3. Fully plug and play api support, without touching the code.
4. Support for any operating system that supports python. Basically Cross Platform.
5. Fully (100%) customizable from configuration. (avoiding the coding mess.)
5. Remote search query.

## 3. Usage

### 1. Choose random local image directory

Lets assume we have number of pictures on `/home/debendra/Pictures/Wallpapers`

```
[debendra@debendra-pc ~]$ auto_wall --image /home/debendra/Pictures/Wallpapers
```
Default wallpaper directory specified in `config.json` will be used if no image source is supplied.

### 2. Choose random remote images

Well `auto_wall` can interact with external image hosting any sites that exists on the WWW, api are fully pluggable from
configuration. (I can say this is the best part.) :-)

You can configure any numbers of image provider just modifying the configuration files without the need to
touch the code but least `JSON` knowledge is required :-).

Image provider must support api endpoint in order to support the external fetch.

1. Create or login into image provider app/website and get auth/access token if required.
2. Paste auth/access token in `config.json` file to the header subsection of `remotes`'s section.
3. Inspect the response body and supply the appropriate `key/pairs` to the `extarct_keys` sub-section of `remotes`'s section.


Currently pexels and unsplash are already configured.


`$ auto_wall --image unsplash`

Above command will fetch the images the unsplash and apply to both screens action. (background, lock screen)

### 3. Neglect specific screen action

Specific screen action can be omitted.

Supply argument as `--no-wall` for wallpaper and `no-lock-screen` for screen saver/lock.

`$ auto_wall --image /home/suraj/bikini_girls --no-lock-screen` :-(

Above command will randomly select images from the path specified and neglect the screen saver/lock.

### 4. Search and apply remote images.

You can also search your desired images.

`$ auto_wall --image pexels --query nature`

Above command will fetch images from the pexels api based on search query and apply accordingly. 

## 4. Configuration Option

As I yield that program is cross platform, accordingly I have provided support as well.

Number of placeholders are available for configurations.

1. `%home_dir%`: can be used for the user's home directory.
2. `%sep%`: directory separator.
3. `%_%`: for spaces.
4. `image%`: pass image path as argument to the OS command.

***Placeholders are case-insensitive.***

***Supply `auto_wall --help`  for more.*** 

## 5. Support

Bugs/issues/Ideas can be dropped in issues section. It really helps.

I would really appreciate if someone puts efforts to support MS Windows.

I don't have MS Windows to tests. Windows needs special configuration
because it does not support other than the `.bmp` format, probably on coding level to convert
to `.bmp` format.

I have tested on linux xfce4 and gnome DE and it runs fine on them, I will collect configurations
required to operate on others too, you can also support as your requirements.
All the commands required for OS can be configured from `oses.json`.


Also I would welcome any contribution. :-)




I have a reason not to organize the code and make it readable, the idea was to make portable as possible,
so it can be really helpful for `bashing` things. Little dirty though. :-)


***PS: This program can be really useful for educational purpose, not so useful for everyone though. :-)***
