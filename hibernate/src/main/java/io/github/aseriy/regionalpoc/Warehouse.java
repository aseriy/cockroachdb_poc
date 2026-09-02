package io.github.aseriy.regionalpoc;

import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "warehouse")
public class Warehouse {

    @Id
    private UUID id;

    @Column(name = "region")
    private String region;

    @Column(name = "location")
    private String location;

    public UUID getId() {
        return id;
    }

    public String getRegion() {
        return region;
    }

    public String getLocation() {
        return location;
    }
}
