#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "VeyrCombatTypes.h"
#include "VeyrKnight.generated.h"

class AVeyrDragon;
class UCameraComponent;
class UPointLightComponent;
class USpringArmComponent;
class UStaticMesh;
class UStaticMeshComponent;
class USceneComponent;
class UPrimitiveComponent;
class APlayerController;
class UVeyrSkeletalPresentation;
class UVeyrVisualDefinition;
class UPoseableMeshComponent;
class UMaterialInterface;
class UMaterialInstanceDynamic;

/** Native combat owner. Primitive presentation is explicitly temporary pending Customuse. */
UCLASS()
class VEYR_API AVeyrKnight : public ACharacter
{
    GENERATED_BODY()

public:
    AVeyrKnight();
    virtual void Tick(float DeltaSeconds) override;
    // Owner removed jumping; also reject inherited/Blueprint jump requests.
    virtual bool CanJumpInternal_Implementation() const override { return false; }
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat") float Health = 100.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat") float Stamina = 100.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat") int32 HealingCharges = 4;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat") EVeyrKnightAction Action = EVeyrKnightAction::Ready;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat") TObjectPtr<AVeyrDragon> Boss;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat") bool bLockedOn = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat") bool bTwoHanded = false;
    UFUNCTION(BlueprintPure, Category="Combat") bool IsTwoHanded() const { return bTwoHanded; }
    UFUNCTION(BlueprintCallable, Category="Combat") void ToggleGrip();
    UFUNCTION(BlueprintCallable, Category="Combat") void TryDirectionalBlink();
    UFUNCTION(BlueprintCallable, Category="Input") void SetSprintRequested(bool bHeld) { bSprintHeld=bHeld; }
    UFUNCTION(BlueprintCallable, Category="Input") void PressPrimaryAttack();
    UFUNCTION(BlueprintCallable, Category="Input") void ReleasePrimaryAttack();
    UFUNCTION(BlueprintPure, Category="Input") bool IsSprinting() const { return bSprintHeld; }
    UFUNCTION(BlueprintPure, Category="Combat") bool IsChangingGrip() const { return Action==EVeyrKnightAction::GripToTwoHand||Action==EVeyrKnightAction::GripToOneHand; }
    /** Elapsed trimmed source seconds, including a primary-combo segment offset. */
    UFUNCTION(BlueprintPure, Category="Combat") float GetActionSourceSeconds() const;
    UFUNCTION(BlueprintPure, Category="Combat") FName GetActionPresentationClip() const { return ActionPresentationClip; }
    void SuspendForPauseMenu();
    void ResumeFromPauseMenu(bool bRecapture);
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input",meta=(ClampMin="0.25",ClampMax="2.5")) float MouseSensitivity=1.f;


    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 LightAttacks = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 HeavyAttacks = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 Rolls = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 DodgedHits = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 HitsTaken = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 GuardedHits = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 GuardBreaks = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 SuccessfulHeals = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 SuccessfulJumps = 0;
    /** Sampled from the preceding resolved spring-arm frame; walls may legitimately compress it. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float CameraResolvedDistance = 720.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float CameraSeverelyCompressedSeconds = 0.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 CameraHiddenProxyParts = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float CameraFloorClearance=220.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float CameraPitchCeiling=0.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float CameraFramingArm=720.f;

    UFUNCTION(BlueprintPure, Category="Combat") bool IsDead() const { return Health <= 0.f; }
    UFUNCTION(BlueprintPure, Category="Combat") bool IsGrounded() const;
    UFUNCTION(BlueprintPure, Category="Combat") bool IsRollingInvulnerable() const;
    UFUNCTION(BlueprintPure, Category="Combat") bool IsGuardBroken() const { return bGuardBroken; }
    UFUNCTION(BlueprintPure, Category="Combat") float GetActionElapsed() const { return ActionElapsed; }
    UFUNCTION(BlueprintPure, Category="Combat") float GetActionDuration() const { return ActionDuration; }
    UFUNCTION(BlueprintPure, Category="Combat") float GetSwordContactTime() const;
    UFUNCTION(BlueprintPure, Category="Combat") float GetAttackDuration(bool bHeavy) const;
    UFUNCTION(BlueprintPure, Category="Combat") float GetAttackContactTime(bool bHeavy) const;
    UFUNCTION(BlueprintPure, Category="Combat") float GetPlanarSpeed() const;
    UFUNCTION(BlueprintPure, Category="Combat") FVector GetFootLocation() const;
    UFUNCTION(BlueprintPure, Category="Combat") FVector GetRollDirection() const { return RollDirection; }
    UFUNCTION(BlueprintPure, Category="Input") bool IsMouseCaptured() const { return bMouseCaptured; }
    UFUNCTION(BlueprintPure, Category="Input") bool IsReplayControlled() const { return bReplayControlled; }
    UFUNCTION(BlueprintPure, Category="Input") bool HasEnteredEncounter() const { return bHasEverCapturedMouse || bReplayControlled; }
    UFUNCTION(BlueprintCallable, Category="Combat") void ApplyBossDamage(float Amount, const FVector& Source, bool bUnblockable = false);
    UFUNCTION(BlueprintCallable, Category="Combat") void TryLightAttack();
    UFUNCTION(BlueprintCallable, Category="Combat") void TryHeavyAttack();
    UFUNCTION(BlueprintCallable, Category="Combat") void TryRoll();
    UFUNCTION(BlueprintCallable, Category="Combat") void TryHeal();
    UFUNCTION(BlueprintCallable, Category="Combat") void TryCombo();
    UFUNCTION(BlueprintCallable, Category="Combat") void TryBackstep();
    UFUNCTION(Exec) void VeyrSetVariants(int32 RunVariant, int32 HeavyVariant, int32 TwoHandHeavyVariant);
    UFUNCTION(Exec) void VeyrBackstep();
    UFUNCTION(Exec) void VeyrCombo();
    UFUNCTION(BlueprintCallable, Category="Combat") void CycleAnimationVariants();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 RunAnimationVariant=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 HeavyAnimationVariant=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 TwoHandHeavyAnimationVariant=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 ComboAttacks=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 RollAttacks=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 BlinkDodges=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 RunStops=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 SuccessfulStrikeWindows=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 CurrentDamageWindow=INDEX_NONE;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bBlinkHidden=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bApprovedNativeDefinitionActive=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bUsingPolishDefinition=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 BlinkEchoCaptures=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") FString BlinkVFXDiagnostic;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bLateralDodgeBlocked=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 RootMotionBlockedCount=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float ActionRootTravelCm=0.f;
    UFUNCTION(BlueprintCallable, Category="Combat") void SetGuard(bool bHeld);
    UFUNCTION(BlueprintCallable, Category="Combat") void ToggleLockOn();
    UFUNCTION(BlueprintCallable, Category="Combat") void RestartIfTerminal();
    UFUNCTION(BlueprintCallable, Category="Presentation") bool ApplyCustomuseVisual(UVeyrVisualDefinition* Definition);

    /** Input-level test hook; never writes health, action clocks, position or boss state. */
    void SetReplayInput(const FVector& WorldMove, bool bLight, bool bHeavy, bool bRoll, bool bHeal, bool bJump, bool bGuard);
    void ClearReplayInput();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera") TObjectPtr<USpringArmComponent> CameraBoom;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera") TObjectPtr<UCameraComponent> CombatCamera;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Temporary Art") TObjectPtr<USceneComponent> TemporaryVisual;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Presentation") TObjectPtr<UVeyrSkeletalPresentation> ImportedPresentation;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") TObjectPtr<UVeyrVisualDefinition> CustomuseVisualDefinition;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bImportedPresentationActive=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bRequestedPresentationClipSampled=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bPresentationUsingFallback=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") FName RequestedPresentationClip=NAME_None;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") FString PresentationDiagnostic;
    /** Native centimeters/second represented by each authored locomotion clip. */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Presentation") TMap<FName,float> PresentationNominalSpeeds;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") FName RequestedLowerPresentationClip=NAME_None;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float PresentationLowerWeight=0.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float PresentationJumpPhase=0.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bHealFlaskVisible=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") FString HealFlaskDiagnostic;

    // Knight completion 2026-10-28. Lock-on locomotion faces the boss and selects Backpedal/strafe
    // clips by local move direction; -VeyrNoLockOnStrafe restores the old orient-to-movement walk.
    UFUNCTION(BlueprintPure, Category="Combat") bool IsLockOnStrafing() const;
    /** 0 forward, 1 back, 2 left, 3 right (actor-local move direction while lock-on strafing). */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 LockOnMoveDirection=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bLockOnStrafeEnabled=true;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bDirectionalStaggerEnabled=true;
    /** Seconds of the Run<->RunStop pose blend (measured join, Local/knight-review-20261028/data). */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float RunStopBlendSeconds=.30f;
    /** Round 2: blend seconds when entering/leaving lock-on locomotion (-VeyrLockOnBlend=). */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float LockOnBlendSeconds=.30f;
    /** Round 2: sword placed from the right hand during pose blends (-VeyrNoWeaponGripLock restores the old path). */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bWeaponGripLockEnabled=true;
    /** Test record (no gameplay effect): blink hidden windows [0.18, 0.34) s of action time traversed by the action
     *  clock, with world-time start/end interpolated inside the frame that crossed each edge. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 BlinkHiddenWindows=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float LastBlinkHiddenStartWorld=-1.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float LastBlinkHiddenEndWorld=-1.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float LastBlinkLongestFrame=0.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bLastBlinkHiddenFrameRendered=false;
    /** Blend-proof tooling (read-only; no gameplay effect). Pose-blend state of the last presentation update. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") int32 ProofTransitionSerial=0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float ProofBlendAlpha=1.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") bool bProofBlendActive=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") FName ProofBlendFromClip=NAME_None;
    /** The equipped sword mesh's actual world transform (what the camera sees); false when it is hidden or absent. */
    bool GetProofWeaponWorld(FTransform& Out) const;
    /** Action-time seconds at which the RollAttack roll prefix ends and its strike window ends (false without the clip). */
    bool GetProofRollAttackTimes(float& OutRollPrefixEnd,float& OutStrikeEnd) const;
    /** Front, back, left, right: hits that selected a directional stagger clip. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") TArray<int32> DirectionalStaggers;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") FName LastStaggerClip=NAME_None;
    /** Hit source direction relative to the knight's facing, degrees: 0 front, +90 right, -90 left. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Evidence") float LastStaggerSourceYaw=0.f;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY() TObjectPtr<UPointLightComponent> ReadabilityFill;
    UPROPERTY() TObjectPtr<USceneComponent> SwordPivot;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> BoatWeapon;
    bool bBoatReleased=false;
    float BoatReleaseTime=0.f;
    FTransform BoatReleaseStart,BoatReleaseRest;
    bool GetWeaponSweep(FVector& Base,FVector& Tip);
    void UpdateEquippedWeapon();
    UPROPERTY() TObjectPtr<UStaticMeshComponent> LeftLeg;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> RightLeg;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> ProxyParts;
    UPROPERTY() TObjectPtr<UStaticMeshComponent> ApprovedHealCup;
    UPROPERTY() TArray<TObjectPtr<UPoseableMeshComponent>> BlinkEchoBodies;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> BlinkEchoWeapons;
    UPROPERTY() TArray<TObjectPtr<UMaterialInstanceDynamic>> BlinkEchoMaterials;
    UPROPERTY() TObjectPtr<UMaterialInterface> BlinkEchoMaterial;
    // Shadow-dash blink (owner 2026-10-31): 0 departure, 1 arrival, 2 live shade that travels while the knight is
    // hidden, 3..6 trail stills dropped along the path.
    static constexpr int32 BlinkEchoCount=7,BlinkEchoShade=2,BlinkEchoTrailFirst=3;
    bool bBlinkEchoCaptured[BlinkEchoCount]={};
    float BlinkEchoStarted[BlinkEchoCount]={};
    void ClearBlinkEchoes();
    void UpdateBlinkEchoes();
    bool CaptureBlinkEcho(int32 Index,float SourceSeconds,const FLinearColor& Tint,float Opacity,bool bCountEvidence);
    FVector RootTranslationAt(float Seconds) const;
    UPROPERTY() TObjectPtr<USceneComponent> HealFlaskRoot;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> HealFlaskParts;

    float BlinkCooldownRemaining=0.f;
    bool bWasRunning=false;
    bool bSprintHeld=false;
    bool bPrimaryAttackHeld=false,bPrimaryAttackBuffered=false,bPrimaryChainActive=false,bStartingPrimaryStep=false;
    int32 PrimaryChainStep=0,PrimarySwingBase=0;
    float PrimarySourceOffset=0.f;
    float BlinkDirectionYaw=0.f;
    FVector BlinkRequestedDirection=FVector::ZeroVector;
    bool bActionRootBlocked=false;
    FName LastLocomotionClip=NAME_None;
    FName PendingStaggerClip=NAME_None;
    bool bTransitionInvolvesRunStop=false;
    bool bLockOnStrafingLastFrame=false;
    bool bTransitionLockOnEdge=false;
    bool bBlinkHiddenStartRecorded=false,bBlinkHiddenEndRecorded=false;
    bool bWeaponGripBlendActive=false;
    float WeaponGripAlpha=1.f;
    FTransform WeaponGripSource=FTransform::Identity,WeaponGripTarget=FTransform::Identity;
    bool GetWeaponSocketWorld(FTransform& Out);
    FName ChooseStaggerClip(const FVector& Source);
    FName PickLockOnClip(FName Preferred, FName Fallback) const;
    float LockOnSpeedCap(FName Clip) const;
    FName ActionPresentationClip=NAME_None;
    TSet<int32> ContactedDamageWindows;
    int32 ActionSwingBase=0;
    bool bPreserveRollPrefix=false;
    float GripTransitionRemaining = 0.f;
    float BufferedAttackRemaining = 0.f;
    bool bBufferedHeavy = false;
    bool bSwingTwoHanded = false;
    float ActionElapsed = 0.f;
    float ActionDuration = 0.f;
    float RegenDelay = 0.f;
    float DamageGrace = 0.f;
    float VisualClock = 0.f;
    float PresentationLocomotionTime = 0.f;
    float PresentationLowerTime = 0.f;
    float PresentationJumpLaunchSpeed = 580.f;
    float PresentationRollYaw = 0.f;
    FName PresentationLowerClip=NAME_None;
    FName PresentationTransitionLowerClip=NAME_None;
    FName FailedPresentationClip=NAME_None;
    FString FailedPresentationReason;
    bool bIdleFallbackRejected=false;
    FName PresentationTransitionClip=NAME_None;
    float PresentationTransitionStarted=0.f;
    float PresentationPreviousActionElapsed=-1.f;
    bool bPresentationTransitionActive=false;
    float CameraDistance = 560.f;
    float ManualCameraRemaining=0.f;
    float BladeContactRadius=18.f;
    float CameraFloorZ = 0.f;
    float CameraObstructionHold = 0.f;
    float LockHeadBlend = 0.f;
    float FlightCameraBlend = 0.f;
    TWeakObjectPtr<APlayerController> OcclusionController;
    TMap<TWeakObjectPtr<UPrimitiveComponent>, float> CameraHiddenParts;
    TWeakObjectPtr<APlayerController> MouseInputController;
    int32 SwingId = 0;
    bool bContactSent = false;
    bool bPreviousBladePoseValid=false;
    FVector PreviousBladeBase=FVector::ZeroVector, PreviousBladeTip=FVector::ZeroVector;
    bool bHealGranted = false;
    bool bGuardRequested = false;
    bool bGuardBroken = false;
    bool bForwardHeld = false, bBackHeld = false, bLeftHeld = false, bRightHeld = false;
    bool bReplayControlled = false;
    bool bMouseCaptured = false;
    bool bHasEverCapturedMouse = false;
    bool bMouseCaptureConfirmationPending = false;
    bool bResumeCapturePending = false;
    uint64 ResumeCaptureRequestedFrame = 0,MouseLookEnableAfterFrame = 0;
    double MouseLookEnableAfterTime = 0.;
    float MouseCaptureRequestedAt = 0.f;
    bool bReplayJumpHeld = false;
    bool bReplayLight = false, bReplayHeavy = false, bReplayRoll = false, bReplayHeal = false, bReplayJump = false, bReplayGuard = false;
    FVector ReplayMove = FVector::ZeroVector;
    FVector MoveIntent = FVector::ZeroVector;
    FVector RollDirection = FVector::ForwardVector;

    bool IsTerminal() const;
    bool IsAttackAction() const;
    bool IsBlinkAction() const;
    bool IsRollPrefix() const;
    bool HasVisualClip(FName Name) const;
    float VisualClipPlayRate(FName Name) const;
    float VisualClipDuration(FName Name,float Fallback) const;
    float VisualClipSpeed(FName Name) const;
    FName ChooseAttackClip(bool bHeavy) const;
    FName ResolveActionClip(EVeyrKnightAction NewAction) const;
    bool TryBlink(bool bLeft);
    void ApplyAuthoredRootMotion(float PreviousSeconds,float NewSeconds);
    void ResolveAttackWindows(float PreviousSeconds);
    void ComboPressed();
    void VariantPressed();
    void SprintPressed();
    void SprintReleased();
    void BlinkPressed();
    void PausePressed();
    bool StartPrimaryStep(int32 Step);
    FVector AuthoredRootDisplacementWorld(const FVector& Delta) const;
    bool CanStartGroundedAction() const;
    void BeginAction(EVeyrKnightAction NewAction, float Duration);
    void FinishAction();
    void AdvanceCombat(float DeltaSeconds);
    void UpdateMovement(float DeltaSeconds);
    void UpdateCamera(float DeltaSeconds);
    void UpdateCameraOcclusion(float DeltaSeconds);
    void RestoreCameraOcclusion();
    void UpdateTemporaryPresentation(float DeltaSeconds);
    void UpdateImportedPresentation(float DeltaSeconds=0.f);
    FName SelectDirectionalLocomotion(bool bAllowRun) const;
    void UpdateHealFlask();
    void SetPresentationDiagnostic(const FString& Diagnostic);
    UStaticMeshComponent* CreateProxyPart(const TCHAR* Name, UStaticMesh* Mesh, USceneComponent* Parent, const FVector& Location, const FVector& Size);
    bool MouseLookReady() const;
    void LookYaw(float Value);
    void LookPitch(float Value);
    void ZoomIn();
    void ZoomOut();
    void GuardPressed();
    void GuardReleased();
    void ForwardPressed(); void ForwardReleased();
    void BackPressed(); void BackReleased();
    void LeftPressed(); void LeftReleased();
    void RightPressed(); void RightReleased();
    bool HumanInputEnabled() const;
    void UpdateMouseCapture();
    void CaptureMouseOrAttack();
    void BeginControlFromKeyboard();
    void ReleaseMouse();
    void GripPressed();
    void LightPressed(); void HeavyPressed(); void RollPressed();
    void HealPressed(); void LockPressed();
};
