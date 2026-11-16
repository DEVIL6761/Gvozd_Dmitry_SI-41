import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.StringJoiner;

public class ShiftPlanFixed {
    private static final DateTimeFormatter DATE_FORMAT =
            DateTimeFormatter.ofPattern("dd.MM.yyyy");
    private static final List<String> log =
            Collections.synchronizedList(new ArrayList<>());

    public static void main(String[] args) throws Exception {
        List<Brigade> brigades = sampleBrigades();
        String actual = make(brigades, 2, Path.of("наряд.txt"));
        check("характеризующий тест: состав и порядок наряда",
                "Петров; Козлов".equals(actual));
        check("исходный список не изменяется", brigades.size() == 4);
        check("запись в файл выполнена",
                Files.readString(Path.of("наряд.txt")).equals(actual));
        check("запись события в журнал",
                !log.isEmpty() && log.get(log.size() - 1).contains("наряд сформирован"));
        check("порядок подходящих бригад сохранён",
                actual.equals(String.join("; ", Arrays.asList("Петров", "Козлов"))));

        checkThrows("отрицательное число бригад отклоняется",
                () -> make(sampleBrigades(), -1, Path.of("test.txt")));
        checkThrows("недостаточное число бригад отклоняется",
                () -> make(sampleBrigades(), 3, Path.of("test.txt")));
        checkThrows("null вместо списка отклоняется",
                () -> make(null, 1, Path.of("test.txt")));
        checkThrows("null-элемент отклоняется",
                () -> make(Arrays.asList((Brigade) null), 0, Path.of("test.txt")));
    }

    private static List<Brigade> sampleBrigades() {
        return new ArrayList<>(Arrays.asList(
                new Brigade("Иванов", 11.0, true),
                new Brigade("Петров", 0.0, true),
                new Brigade("Сидоров", 4.5, false),
                new Brigade("Козлов", 8.0, true)));
    }

    public static String make(List<Brigade> brigades, int need, Path output)
            throws IOException {
        if (brigades == null) {
            throw new IllegalArgumentException("Список бригад не должен быть null");
        }
        if (output == null) {
            throw new IllegalArgumentException("Путь к файлу не должен быть null");
        }
        if (need < 0) {
            throw new IllegalArgumentException("Число требуемых бригад не может быть отрицательным");
        }

        List<Brigade> eligible = new ArrayList<>();
        for (Brigade brigade : brigades) {
            if (brigade == null) {
                throw new IllegalArgumentException("Список содержит null вместо бригады");
            }
            if (!Double.isFinite(brigade.hoursPerShift) || brigade.hoursPerShift < 0) {
                throw new IllegalArgumentException("Часы смены должны быть конечным неотрицательным числом");
            }
            if (brigade.hoursPerShift <= 10.0 && brigade.admitted) {
                eligible.add(brigade);
            }
        }
        if (need > eligible.size()) {
            throw new IllegalArgumentException(
                    "Запрошено бригад: " + need + ", доступно: " + eligible.size());
        }

        StringJoiner joiner = new StringJoiner("; ");
        for (int i = 0; i < need; i++) {
            joiner.add(eligible.get(i).lastName);
        }
        String result = joiner.toString();
        Files.writeString(output, result);
        log.add(DATE_FORMAT.format(LocalDate.now()) + " наряд сформирован");
        return result;
    }

    private static void check(String name, boolean condition) {
        if (condition) {
            System.out.println("[OK] " + name);
        } else {
            System.out.println("[FAIL] " + name);
            throw new AssertionError(name);
        }
    }

    private static void checkThrows(String name, ThrowingRunnable action) throws Exception {
        try {
            action.run();
            check(name, false);
        } catch (IllegalArgumentException expected) {
            check(name, true);
        }
    }

    @FunctionalInterface
    private interface ThrowingRunnable {
        void run() throws Exception;
    }
}

class Brigade {
    String lastName;
    double hoursPerShift;
    boolean admitted;

    Brigade(String lastName, double hoursPerShift, boolean admitted) {
        if (lastName == null || lastName.isBlank()) {
            throw new IllegalArgumentException("Фамилия не должна быть пустой");
        }
        this.lastName = lastName;
        this.hoursPerShift = hoursPerShift;
        this.admitted = admitted;
    }
}
