package com.pressureplatemines.init;

import com.pressureplatemines.PressurePlateMines;
import com.pressureplatemines.block.PressurePlateMineBlock;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(PressurePlateMines.MODID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(PressurePlateMines.MODID);

    // List of all mine entries for easy iteration (recipes, creative tab, etc.)
    public static final List<MineEntry> ALL_MINES = new ArrayList<>();

    // --- Stone variants ---
    public static final MineEntry STONE_MINE = registerMine("stone_mine", "Stone Mine",
            SoundType.STONE, 1.5f, 6.0f, "stone");
    public static final MineEntry COBBLESTONE_MINE = registerMine("cobblestone_mine", "Cobblestone Mine",
            SoundType.STONE, 2.0f, 6.0f, "cobblestone");
    public static final MineEntry DEEPSLATE_MINE = registerMine("deepslate_mine", "Deepslate Mine",
            SoundType.DEEPSLATE, 3.0f, 6.0f, "deepslate");
    public static final MineEntry COBBLED_DEEPSLATE_MINE = registerMine("cobbled_deepslate_mine", "Cobbled Deepslate Mine",
            SoundType.DEEPSLATE, 3.5f, 6.0f, "cobbled_deepslate");

    // --- Brick variants ---
    public static final MineEntry STONE_BRICKS_MINE = registerMine("stone_bricks_mine", "Stone Bricks Mine",
            SoundType.STONE, 1.5f, 6.0f, "stone_bricks");
    public static final MineEntry BRICKS_MINE = registerMine("bricks_mine", "Bricks Mine",
            SoundType.STONE, 2.0f, 6.0f, "bricks");

    // --- Dirt / grass variants ---
    public static final MineEntry DIRT_MINE = registerMine("dirt_mine", "Dirt Mine",
            SoundType.GRAVEL, 0.5f, 0.5f, "dirt");
    public static final MineEntry GRASS_BLOCK_MINE = registerMine("grass_block_mine", "Grass Block Mine",
            SoundType.GRASS, 0.6f, 0.6f, "grass_block");

    // --- Sand variants ---
    public static final MineEntry SAND_MINE = registerMine("sand_mine", "Sand Mine",
            SoundType.SAND, 0.5f, 0.5f, "sand");
    public static final MineEntry GRAVEL_MINE = registerMine("gravel_mine", "Gravel Mine",
            SoundType.GRAVEL, 0.6f, 0.6f, "gravel");

    // --- Wood variants ---
    public static final MineEntry OAK_PLANKS_MINE = registerMine("oak_planks_mine", "Oak Planks Mine",
            SoundType.WOOD, 2.0f, 3.0f, "oak_planks");
    public static final MineEntry SPRUCE_PLANKS_MINE = registerMine("spruce_planks_mine", "Spruce Planks Mine",
            SoundType.WOOD, 2.0f, 3.0f, "spruce_planks");
    public static final MineEntry BIRCH_PLANKS_MINE = registerMine("birch_planks_mine", "Birch Planks Mine",
            SoundType.WOOD, 2.0f, 3.0f, "birch_planks");
    public static final MineEntry DARK_OAK_PLANKS_MINE = registerMine("dark_oak_planks_mine", "Dark Oak Planks Mine",
            SoundType.WOOD, 2.0f, 3.0f, "dark_oak_planks");

    // --- Ore-look variants ---
    public static final MineEntry IRON_ORE_MINE = registerMine("iron_ore_mine", "Iron Ore Mine",
            SoundType.STONE, 3.0f, 3.0f, "iron_ore");

    // --- Nether variants ---
    public static final MineEntry NETHERRACK_MINE = registerMine("netherrack_mine", "Netherrack Mine",
            SoundType.NETHERRACK, 0.4f, 0.4f, "netherrack");
    public static final MineEntry NETHER_BRICKS_MINE = registerMine("nether_bricks_mine", "Nether Bricks Mine",
            SoundType.NETHER_BRICKS, 2.0f, 6.0f, "nether_bricks");

    // --- End variant ---
    public static final MineEntry END_STONE_MINE = registerMine("end_stone_mine", "End Stone Mine",
            SoundType.STONE, 3.0f, 9.0f, "end_stone");

    // --- Polished variants ---
    public static final MineEntry POLISHED_ANDESITE_MINE = registerMine("polished_andesite_mine", "Polished Andesite Mine",
            SoundType.STONE, 1.5f, 6.0f, "polished_andesite");
    public static final MineEntry POLISHED_GRANITE_MINE = registerMine("polished_granite_mine", "Polished Granite Mine",
            SoundType.STONE, 1.5f, 6.0f, "polished_granite");
    public static final MineEntry POLISHED_DIORITE_MINE = registerMine("polished_diorite_mine", "Polished Diorite Mine",
            SoundType.STONE, 1.5f, 6.0f, "polished_diorite");

    private static MineEntry registerMine(String name, String displayName, SoundType sound, float hardness, float resistance, String disguiseBlock) {
        DeferredBlock<Block> block = BLOCKS.register(name, () -> new PressurePlateMineBlock(
                BlockBehaviour.Properties.of()
                        .strength(hardness, resistance)
                        .sound(sound)
                        .noOcclusion()
        ));

        DeferredItem<BlockItem> item = ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));

        MineEntry entry = new MineEntry(name, displayName, block, item, disguiseBlock);
        ALL_MINES.add(entry);
        return entry;
    }

    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
        ITEMS.register(modEventBus);
    }

    /**
     * Holds all info about a mine variant for easy recipe/model generation.
     */
    public record MineEntry(
            String id,
            String displayName,
            DeferredBlock<Block> block,
            DeferredItem<BlockItem> item,
            String disguiseBlock
    ) {}
}
