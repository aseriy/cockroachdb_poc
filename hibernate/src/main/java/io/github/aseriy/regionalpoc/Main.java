package io.github.aseriy.regionalpoc;

import java.util.List;
import java.util.UUID;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.cfg.Configuration;

public class Main {

    private static final Logger POOLING_LOGGER =
            Logger.getLogger("org.hibernate.orm.connections.pooling");

    public static void main(String[] args) {
        POOLING_LOGGER.setLevel(Level.WARNING);

        String url = null;
        for (int i = 0; i < args.length; i++) {
            if (("--url".equals(args[i]) || "-u".equals(args[i])) && i + 1 < args.length) {
                url = args[i + 1];
                i++;
            }
        }
        if (url == null) {
            System.err.println("usage: Main --url|-u <jdbc-url>");
            System.exit(1);
        }

        System.out.println("url: " + url
                .replaceAll("user=[^&]*", "user=****")
                .replaceAll("password=[^&]*", "password=****"));

        Configuration configuration = new Configuration()
                .addAnnotatedClass(Warehouse.class)
                .addAnnotatedClass(GateArrival.class)
                .setProperty("hibernate.connection.url", url)
                .setProperty("hibernate.show_sql", "true");

        try (SessionFactory sessionFactory = configuration.buildSessionFactory();
             Session session = sessionFactory.openSession()) {

            Warehouse warehouse = session
                    .createQuery("from Warehouse", Warehouse.class)
                    .setMaxResults(1)
                    .getSingleResult();
            String crdbRegion = switch (warehouse.getRegion()) {
                case "east" -> "tx1";
                case "west" -> "tx3";
                default -> throw new IllegalStateException(
                        "unexpected warehouse region: " + warehouse.getRegion());
            };
            System.out.println("warehouse: " + warehouse.getId()
                    + " region: " + warehouse.getRegion()
                    + " -> " + crdbRegion);

            runQuery(session, warehouse.getId(), "filter off");

            session.enableFilter(RegionFilterContributor.FILTER_NAME)
                    .setParameter("region", crdbRegion);

            runQuery(session, warehouse.getId(), "filter on ");
        }
    }

    private static void runQuery(Session session, UUID warehouseId, String label) {
        long start = System.nanoTime();
        List<GateArrival> rows = session
                .createQuery("from GateArrival where warehouseId = :x", GateArrival.class)
                .setParameter("x", warehouseId)
                .getResultList();
        long elapsedMs = (System.nanoTime() - start) / 1_000_000;
        System.out.println(label + ": " + rows.size() + " rows in " + elapsedMs + " ms");
    }
}
