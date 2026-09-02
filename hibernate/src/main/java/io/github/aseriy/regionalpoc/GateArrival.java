package io.github.aseriy.regionalpoc;

import java.util.UUID;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "gate_arrival")
public class GateArrival {

    @Id
    private UUID id;

    @Column(name = "warehouse_id")
    private UUID warehouseId;

    @Column(name = "trailer_id")
    private UUID trailerId;

    public UUID getId() {
        return id;
    }

    public UUID getWarehouseId() {
        return warehouseId;
    }

    public UUID getTrailerId() {
        return trailerId;
    }
}
