import { app, BrowserWindow } from "electron";

function createWindow(): void {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
  });

  win.loadURL("about:blank");
}

app.whenReady().then(createWindow);
