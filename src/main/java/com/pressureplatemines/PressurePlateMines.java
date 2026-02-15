package com.pressureplatemines;

import com.pressureplatemines.init.ModBlocks;
import com.pressureplatemines.init.ModCreativeTab;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(PressurePlateMines.MODID)
public class PressurePlateMines {
    public static final String MODID = "pressureplatemines";

    public PressurePlateMines(IEventBus modEventBus) {
        ModBlocks.register(modEventBus);
        ModCreativeTab.register(modEventBus);
    }
}
