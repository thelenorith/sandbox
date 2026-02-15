package com.pressureplatemines.init;

import com.pressureplatemines.PressurePlateMines;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModCreativeTab {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, PressurePlateMines.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MINES_TAB = CREATIVE_TABS.register("mines_tab",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup." + PressurePlateMines.MODID + ".mines_tab"))
                    .icon(() -> new ItemStack(ModBlocks.STONE_MINE.item().get()))
                    .displayItems((parameters, output) -> {
                        for (ModBlocks.MineEntry entry : ModBlocks.ALL_MINES) {
                            output.accept(entry.item().get());
                        }
                    })
                    .build()
    );

    public static void register(IEventBus modEventBus) {
        CREATIVE_TABS.register(modEventBus);
    }
}
