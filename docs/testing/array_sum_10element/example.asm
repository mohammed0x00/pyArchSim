.data
  array0:   .word  0, 2, 4, 6, 8, 10, 12, 14, 16, 18
  array1:   .word  1, 3, 5, 7, 9, 11, 13, 15, 17, 19
  array2:   .space 40
  arrayLen: .word  10
.text
  # test
  la    $t7, arrayLen
  lw    $t0, 0($t7)
  la    $t1, array0
  la    $t2, array1
  la    $t3, array2

  addiu $v0, $0, 88 # ROI
  syscall

  beq   $t0, $zero, vvadd_done
vvadd:
  lw    $t4, 0($t1)
  lw    $t5, 0($t2)
  addu  $t4, $t4, $t5
  sw    $t4, 0($t3)
  addiu $t1, $t1, 4
  addiu $t2, $t2, 4
  addiu $t3, $t3, 4
  addiu $t0, $t0, -1
  bne   $t0, $zero, vvadd

vvadd_done:
  addiu $v0, $0, 88
  syscall

  addiu $v0, $0, 10
  syscall
