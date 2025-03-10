import javax.swing.*;
import java.awt.*;

public class CurveEditor extends JFrame {
    private final DrawPanel drawPanel;

    public CurveEditor() {
        super.setTitle("Графический редактор кривых");
        super.setSize(800, 600);
        super.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        Container container = super.getContentPane();
        container.setLayout(new GridLayout(3,2,2,2));

        drawPanel = new DrawPanel();
        container.add(drawPanel,BorderLayout.CENTER);

        JMenuBar menuBar = new JMenuBar();
        container.add(menuBar);
        JMenu curveMenu = new JMenu("Кривые");
        container.add(curveMenu);
        String[] curveOptions = {"Метод интерполяции Эрмита", "Формы Безье", "Сглаживание кривых методом B-сплайнов"};
        for (String option : curveOptions) {
            JMenuItem item = new JMenuItem(option);
            item.addActionListener(e -> drawPanel.setCurveType(option)); // Обработчик выбора
            curveMenu.add(item);
        }
        menuBar.add(curveMenu);

        JButton clearButton = new JButton("Очистить экран");
        clearButton.addActionListener(e -> drawPanel.clearPoints());
        menuBar.add(clearButton);
        setJMenuBar(menuBar);
    }
}
