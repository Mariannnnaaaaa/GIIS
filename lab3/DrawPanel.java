import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;

class DrawPanel extends JPanel {
    private final ArrayList<Point> points = new ArrayList<>();
    private String curveType = "Метод интерполяции Эрмита";
    private final double[][] hermiteMatrix = {
            {2, -2, 1, 1},
            {-3, 3, -2, -1},
            {0, 0, 1, 0},
            {1, 0, 0, 0}
    };

    public void clearPoints() {
        points.clear();
        repaint();
    }


    public DrawPanel() {
        addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                points.add(e.getPoint());
                repaint();
            }
        });
        addMouseMotionListener(new MouseMotionAdapter() {
            public void mouseDragged(MouseEvent e) {
                for (Point p : points) {
                    if (p.distance(e.getPoint()) < 10) {
                        p.setLocation(e.getPoint());
                        repaint();
                        break;
                    }
                }
            }
        });
        addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                if (SwingUtilities.isRightMouseButton(e)) {
                    points.removeIf(p -> p.distance(e.getPoint()) < 10);
                    repaint();
                }
            }
        });
    }

    public void setCurveType(String type) {
        this.curveType = type;
        repaint();
    }

    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        g.setColor(Color.BLACK);

        for (Point p : points) {
            g.fillOval(p.x - 3, p.y - 3, 6, 6);
        }

        if (points.size() > 1) {
            g.setColor(Color.RED);

            for (int i = 0; i < points.size() - 1; i++) {
                Point p1 = points.get(i);
                Point p2 = points.get(i + 1);
                g.drawLine(p1.x, p1.y, p2.x, p2.y);
            }

            switch (curveType) {
                case "Метод интерполяции Эрмита":
                    drawHermiteCurve(g);
                    break;
                case "Формы Безье":
                    drawBezierCurve(g);
                    break;
                case "Сглаживание кривых методом B-сплайнов":
                    drawBSpline(g);
                    break;
            }
        }
    }

    private void drawHermiteCurve(Graphics g) {
        if (points.size() < 2) return;

        double[][] tangents = new double[points.size()][2];

        for (int i = 0; i < points.size(); i++) {
            if (i == 0) {
                tangents[i][0] = points.get(i + 1).x - points.get(i).x;
                tangents[i][1] = points.get(i + 1).y - points.get(i).y;
            } else if (i == points.size() - 1) {
                tangents[i][0] = points.get(i).x - points.get(i - 1).x;
                tangents[i][1] = points.get(i).y - points.get(i - 1).y;
            } else {
                tangents[i][0] = (points.get(i + 1).x - points.get(i - 1).x) / 2;
                tangents[i][1] = (points.get(i + 1).y - points.get(i - 1).y) / 2;
            }
        }

        for (int i = 0; i < points.size() - 1; i++) {
            Point p0 = points.get(i);
            Point p1 = points.get(i + 1);
            double[] tangent0 = tangents[i];
            double[] tangent1 = tangents[i + 1];

            for (double t = 0; t <= 1; t += 0.01) {
                double[] T = {t * t * t, t * t, t, 1};
                double[] resultX = multiplyMatrix(T, hermiteMatrix, p0, p1, tangent0, tangent1, 0);
                double[] resultY = multiplyMatrix(T, hermiteMatrix, p0, p1, tangent0, tangent1, 1);
                int x = (int) (resultX[0] + resultX[1] + resultX[2] + resultX[3]);
                int y = (int) (resultY[0] + resultY[1] + resultY[2] + resultY[3]);
                g.fillOval(x, y, 2, 2);
            }
        }
    }

    private double[] multiplyMatrix(double[] T, double[][] H, Point p0, Point p1, double[] tangent0, double[] tangent1, int col) {
        double[] result = new double[4];
        double[][] G = {{p0.x, p0.y}, {p1.x, p1.y}, {tangent0[0], tangent0[1]}, {tangent1[0], tangent1[1]}};

        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                result[i] += T[j] * H[j][i];
            }
            result[i] *= G[i][col];
        }
        return result;
    }

    private void drawBezierCurve(Graphics g) {
        if (points.size() < 4) return;

        Point p0 = points.get(0);
        Point p1 = points.get(1);
        Point p2 = points.get(2);
        Point p3 = points.get(3);

        double[][] bezierMatrix = {
                {-1, 3, -3, 1},
                {3, -6, 3, 0},
                {-3, 3, 0, 0},
                {1, 0, 0, 0}
        };

        double[][] Px = {{p0.x}, {p1.x}, {p2.x}, {p3.x}};
        double[][] Py = {{p0.y}, {p1.y}, {p2.y}, {p3.y}};

        for (double t = 0; t <= 1; t += 0.01) {
            double[] T = {t * t * t, t * t, t, 1};  // Вектор T

            double x = multiplyMatrix(T, bezierMatrix, Px);
            double y = multiplyMatrix(T, bezierMatrix, Py);

            g.fillOval((int) x, (int) y, 2, 2);
        }
    }

    private double multiplyMatrix(double[] T, double[][] M, double[][] P) {
        double[] temp = new double[4];

        for (int i = 0; i < 4; i++) {
            temp[i] = 0;
            for (int j = 0; j < 4; j++) {
                temp[i] += T[j] * M[j][i];
            }
        }

        double result = 0;
        for (int i = 0; i < 4; i++) {
            result += temp[i] * P[i][0];
        }

        return result;
    }


    private void drawBSpline(Graphics g) {
        if (points.size() < 4) return;

        double[][] bsplineMatrix = {
                {-1, 3, -3, 1},
                {3, -6, 3, 0},
                {-3, 0, 3, 0},
                {1, 4, 1, 0}
        };

        for (int i = 1; i < points.size() - 2; i++) {
            Point p0 = points.get(i - 1);
            Point p1 = points.get(i);
            Point p2 = points.get(i + 1);
            Point p3 = points.get(i + 2);

            double[][] Gx = {{p0.x}, {p1.x}, {p2.x}, {p3.x}};
            double[][] Gy = {{p0.y}, {p1.y}, {p2.y}, {p3.y}};

            for (double t = 0; t <= 1; t += 0.01) {
                double[] T = {t * t * t, t * t, t, 1};

                double x = multiplyMatrix(T, bsplineMatrix, Gx) / 6.0;
                double y = multiplyMatrix(T, bsplineMatrix, Gy) / 6.0;

                g.fillOval((int) x, (int) y, 2, 2);
            }
        }
    }
}