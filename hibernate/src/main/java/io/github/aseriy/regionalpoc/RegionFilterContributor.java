package io.github.aseriy.regionalpoc;

import java.util.Map;

import org.hibernate.boot.ResourceStreamLocator;
import org.hibernate.boot.spi.AdditionalMappingContributions;
import org.hibernate.boot.spi.AdditionalMappingContributor;
import org.hibernate.boot.spi.InFlightMetadataCollector;
import org.hibernate.boot.spi.MetadataBuildingContext;
import org.hibernate.engine.spi.FilterDefinition;
import org.hibernate.mapping.PersistentClass;
import org.hibernate.metamodel.mapping.JdbcMapping;

public class RegionFilterContributor implements AdditionalMappingContributor {

    public static final String FILTER_NAME = "regionFilter";
    public static final String FILTER_CONDITION = "crdb_region = :region";

    @Override
    public void contribute(
            AdditionalMappingContributions contributions,
            InFlightMetadataCollector metadata,
            ResourceStreamLocator resourceStreamLocator,
            MetadataBuildingContext buildingContext) {
        JdbcMapping stringType = metadata.getTypeConfiguration()
                .getBasicTypeRegistry()
                .getRegisteredType(String.class);
        metadata.addFilterDefinition(new FilterDefinition(
                FILTER_NAME,
                FILTER_CONDITION,
                Map.of("region", stringType)
        ));

        PersistentClass gateArrival = metadata.getEntityBindingMap()
                .get(GateArrival.class.getName());
        gateArrival.addFilter(FILTER_NAME, FILTER_CONDITION, true, null, null);
    }
}
