package com.pressureplatemines.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.PrimedTnt;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.List;

/**
 * A block that looks like a normal block but acts as a pressure plate.
 * When an entity steps on it, it triggers a TNT explosion.
 */
public class PressurePlateMineBlock extends Block {
    public static final BooleanProperty POWERED = BlockStateProperties.POWERED;

    // Full block shape - it looks like a normal block
    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 16, 16);
    // Touch area on top of the block (slightly above the block surface to detect entities standing on it)
    private static final AABB TOUCH_AABB = new AABB(0.0, 1.0, 0.0, 1.0, 1.25, 1.0);

    private final float explosionPower;

    public PressurePlateMineBlock(Properties properties) {
        this(properties, 4.0F); // Default TNT power
    }

    public PressurePlateMineBlock(Properties properties, float explosionPower) {
        super(properties);
        this.explosionPower = explosionPower;
        this.registerDefaultState(this.stateDefinition.any().setValue(POWERED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(POWERED);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return this.defaultBlockState().setValue(POWERED, false);
    }

    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        if (!level.isClientSide && entity instanceof LivingEntity && !state.getValue(POWERED)) {
            activate(state, level, pos, entity);
        }
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        if (!level.isClientSide && entity instanceof LivingEntity && !state.getValue(POWERED)) {
            activate(state, level, pos, entity);
        }
        super.stepOn(level, pos, state, entity);
    }

    @Override
    public void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock, BlockPos neighborPos, boolean movedByPiston) {
        // Also trigger if receiving redstone signal (like normal TNT)
        if (!level.isClientSide && level.hasNeighborSignal(pos) && !state.getValue(POWERED)) {
            activate(state, level, pos, null);
        }
    }

    private void activate(BlockState state, Level level, BlockPos pos, Entity triggerEntity) {
        // Mark as powered to prevent double-activation
        level.setBlock(pos, state.setValue(POWERED, true), 3);

        // Play click sound like a pressure plate
        level.playSound(null, pos, SoundEvents.STONE_PRESSURE_PLATE_CLICK_ON, SoundSource.BLOCKS, 0.3F, 0.6F);

        // Schedule the explosion with a short fuse delay (10 ticks = 0.5 seconds)
        level.scheduleTick(pos, this, 10);
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (state.getValue(POWERED)) {
            explode(level, pos);
        }
    }

    private void explode(Level level, BlockPos pos) {
        // Remove the block
        level.setBlock(pos, Blocks.AIR.defaultBlockState(), 3);

        // Play TNT ignite sound
        level.playSound(null, pos, SoundEvents.TNT_PRIMED, SoundSource.BLOCKS, 1.0F, 1.0F);

        // Create the explosion at the block position
        level.explode(
                null,                           // no entity source
                pos.getX() + 0.5,              // center X
                pos.getY() + 0.5,              // center Y
                pos.getZ() + 0.5,              // center Z
                explosionPower,                 // power (same as TNT)
                Level.ExplosionInteraction.TNT  // behaves like TNT
        );
    }

    // Redstone signal output when activated (like a pressure plate)
    @Override
    public boolean isSignalSource(BlockState state) {
        return state.getValue(POWERED);
    }

    @Override
    public int getSignal(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return state.getValue(POWERED) ? 15 : 0;
    }

    @Override
    public int getDirectSignal(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return state.getValue(POWERED) && direction == Direction.UP ? 15 : 0;
    }
}
