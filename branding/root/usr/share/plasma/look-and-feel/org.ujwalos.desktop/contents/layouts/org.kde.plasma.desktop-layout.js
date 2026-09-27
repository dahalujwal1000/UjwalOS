loadTemplate("org.kde.plasma.desktop.defaultPanel");

const desktops = desktopsForActivity(currentActivity());
for (let index = 0; index < desktops.length; index++) {
    desktops[index].wallpaperPlugin = "org.kde.image";
}
