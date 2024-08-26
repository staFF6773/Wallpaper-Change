import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.Timer;
import java.util.TimerTask;

public class WallpaperChangerApp {

    private JFrame frame;
    private JTextField dayWallpaperField;
    private JTextField nightWallpaperField;
    private JTextField dayTimeField;
    private JTextField nightTimeField;
    private String dayWallpaper = "";
    private String nightWallpaper = "";
    private String dayTime = "06:00";
    private String nightTime = "18:00";
    private Timer timer;
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new WallpaperChangerApp().createAndShowGUI());
    }

    private void createAndShowGUI() {
        frame = new JFrame("Wallpaper Changer");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 300);
        frame.setLayout(new BorderLayout());

        JPanel panel = new JPanel();
        panel.setLayout(new GridLayout(6, 2));

        panel.add(new JLabel("Select Day Wallpaper:"));
        JButton selectDayWallpaperButton = new JButton("Browse");
        selectDayWallpaperButton.addActionListener(e -> selectWallpaper(true));
        panel.add(selectDayWallpaperButton);

        panel.add(new JLabel("Select Night Wallpaper:"));
        JButton selectNightWallpaperButton = new JButton("Browse");
        selectNightWallpaperButton.addActionListener(e -> selectWallpaper(false));
        panel.add(selectNightWallpaperButton);

        panel.add(new JLabel("Day wallpaper change time (HH:MM):"));
        dayTimeField = new JTextField(dayTime);
        panel.add(dayTimeField);

        panel.add(new JLabel("Night wallpaper change time (HH:MM):"));
        nightTimeField = new JTextField(nightTime);
        panel.add(nightTimeField);

        JButton saveButton = new JButton("Save Settings");
        saveButton.addActionListener(e -> saveSettings());
        panel.add(saveButton);

        frame.add(panel, BorderLayout.CENTER);

        frame.setVisible(true);
        loadSettings();
        startTimer();
    }

    private void selectWallpaper(boolean isDay) {
        JFileChooser fileChooser = new JFileChooser();
        int result = fileChooser.showOpenDialog(frame);
        if (result == JFileChooser.APPROVE_OPTION) {
            if (isDay) {
                dayWallpaper = fileChooser.getSelectedFile().getAbsolutePath();
            } else {
                nightWallpaper = fileChooser.getSelectedFile().getAbsolutePath();
            }
        }
    }

    private void saveSettings() {
        dayTime = dayTimeField.getText();
        nightTime = nightTimeField.getText();

        try (PrintWriter writer = new PrintWriter(new FileWriter("settings.txt"))) {
            writer.println("day_wallpaper:" + dayWallpaper);
            writer.println("night_wallpaper:" + nightWallpaper);
            writer.println("day_time:" + dayTime);
            writer.println("night_time:" + nightTime);
            JOptionPane.showMessageDialog(frame, "Settings saved successfully.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void loadSettings() {
        File settingsFile = new File("settings.txt");
        if (settingsFile.exists()) {
            try (BufferedReader reader = new BufferedReader(new FileReader(settingsFile))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split(":", 2);
                    if (parts.length == 2) {
                        switch (parts[0]) {
                            case "day_wallpaper":
                                dayWallpaper = parts[1];
                                break;
                            case "night_wallpaper":
                                nightWallpaper = parts[1];
                                break;
                            case "day_time":
                                dayTime = parts[1];
                                dayTimeField.setText(dayTime);
                                break;
                            case "night_time":
                                nightTime = parts[1];
                                nightTimeField.setText(nightTime);
                                break;
                        }
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void startTimer() {
        timer = new Timer();
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                changeWallpaper();
            }
        }, 0, 60000); // Check every minute
    }

    private void changeWallpaper() {
        String currentTime = new SimpleDateFormat("HH:mm").format(new Date());
        if (isDayTime(currentTime)) {
            setWallpaper(dayWallpaper);
        } else {
            setWallpaper(nightWallpaper);
        }
    }

    private boolean isDayTime(String currentTime) {
        return currentTime.compareTo(dayTime) >= 0 && currentTime.compareTo(nightTime) < 0;
    }

    private void setWallpaper(String wallpaperPath) {
        if (wallpaperPath != null && !wallpaperPath.isEmpty()) {
            try {
                String command = "powershell.exe -Command \"Add-Type -TypeDefinition @\' using System; using System.Runtime.InteropServices; public class Wallpaper { [DllImport(\"user32.dll\")] public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni); } @\'; [Wallpaper]::SystemParametersInfo(20, 0, '" + wallpaperPath.replace("\\", "\\\\") + "', 3)\"";
                Runtime.getRuntime().exec(command);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
