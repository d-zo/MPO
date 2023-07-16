program Umat_Triax
   implicit none
   
   ! IMPORTANT: UMAT allows single AND double precision, but some implementations require double precision
   integer, parameter :: dp = selected_real_kind(15)
   !
   integer, parameter :: ndi = 3
   integer, parameter :: nshr = 3
   integer, parameter :: ntens = 6
   integer, parameter :: nstatv = 20
   integer, parameter :: nprops = 16
   real(dp), dimension(ntens) :: ddsddt, drplde, stran
   real(dp), dimension(ntens, ntens) :: ddsdde
   real(dp), dimension(3, 3) :: drot, dfgrd0, dfgrd1
   real(dp), dimension(3) :: coords
   real(dp), dimension(2) :: time
   real(dp), dimension(1) :: predef, dpred
   real(dp) :: sse, spd, scd, rpl, drpldt, temp, dtemp, celent, pnewdt
   integer, dimension(4) :: jstep
   integer :: noel, npt, layer, kspt, kinc
   !
   character(len=80) :: materialname, outfilename
   real(dp), dimension(nprops) :: materialparameters
   real(dp), dimension(nstatv) :: statevariables
   real(dp), dimension(ntens) :: stress
   real(dp), dimension(ntens) :: strain, refstrain
   real(dp), dimension(6) :: intergranular_strain
   real(dp) :: dt, voidratio, triax_pressure
   real(dp) :: fak2, pressure_deviation, compared_strain, numbersign
   real(dp), dimension(5) :: target_strains
   real(dp), parameter :: tolerable_pressure_deviation = 0.000001_dp
   integer, parameter :: maxiter = 50000
   real(dp), dimension(6) :: sim_strains
   integer :: ixx, jxx, istep, num_params
   integer :: idx, filenr, stat, num_target_strains
   logical :: breakall, is_success
   real(dp) :: starttime, endtime

   call Processed_Arguments(materialname=materialname, triax_pressure=triax_pressure, &
      num_target_strains=num_target_strains, target_strains=target_strains, num_params=num_params, &
      materialparameters=materialparameters, voidratio=voidratio, outfilename=outfilename)

   ddsddt = 0.0_dp
   drplde = 0.0_dp
   stran = 0.0_dp
   ddsdde = 0.0_dp
   drot = reshape([(1.0_dp, (0.0_dp, ixx = 1, 3), jxx = 1, 2), 1.0_dp], [3, 3])
   dfgrd0 = drot
   dfgrd1 = drot
   coords = 0.0_dp
   !
   time = [0.001_dp, 0.001_dp]
   predef = 0.0_dp
   dpred = 0.0_dp
   celent = 0.0_dp
   pnewdt = 0.0_dp
   sse = 0.0_dp
   spd = 0.0_dp
   scd = 0.0_dp
   rpl = 0.0_dp
   drpldt = 0.0_dp
   temp = 0.0_dp
   dtemp = 0.0_dp
   !
   jstep = 0
   noel = 0
   npt = 0
   layer = 0
   kspt = 0
   kinc = 0

   ! Time increment to be used
   dt = 0.0001_dp

   ! Give initial stress and strain matrices (in vector form)
   stress = [triax_pressure, triax_pressure, triax_pressure, 0.0_dp, 0.0_dp, 0.0_dp]
   strain = [-1.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]*dt
   statevariables = 0.0_dp
   statevariables(1) = voidratio

   pressure_deviation = abs(tolerable_pressure_deviation*triax_pressure)
   fak2 = 0.0001_dp
   compared_strain = 0.0_dp


   filenr = 20
   open (filenr, file=trim(outfilename), iostat=stat)
   if(stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   ! Write output for start point as well
   write(filenr, '(f12.5, a, f12.5, a, f12.5)') 0.0, '   ', 0.0, '   ', 0.0

   idx = 1
   sim_strains = 0.0_dp
   breakall = .False.

   call cpu_time(starttime)
   triax_cycle : &
   do istep = 1, num_target_strains
      numbersign = (-1.0_dp)**(istep+1)
      triax_compression : &
      do
         if (numbersign*compared_strain > numbersign*target_strains(istep)) then
            exit triax_compression
         end if

         refstrain = numbersign*strain

         call Triax_Step(stress, statevariables, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
            stran, refstrain, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
            ntens, nstatv, materialparameters(1:num_params), num_params, coords, drot, pnewdt, celent, dfgrd0, &
            dfgrd1, noel, npt, layer, kspt, jstep, kinc, fak2, pressure_deviation, maxiter, breakall)

         if (breakall) then
            exit triax_compression
         end if

         sim_strains = sim_strains + refstrain
         compared_strain = abs(sim_strains(1))

         ! Writing: eps1 in %, eps_v in %, q in kPa
         write(filenr, '(f12.5, a, f12.5, a, f12.5)') -100.0_dp*sim_strains(1), '   ', &
               -100.0_dp*sum(sim_strains(1:3)), '   ', -(stress(1) - stress(2))

         idx = idx + 1
         if (idx > maxiter) then
            write(*, *) 'Error: Maximum number of specified iterations reached'
            exit triax_compression
         end if
      end do triax_compression
   end do triax_cycle
   call cpu_time(endtime)
   print '("Elapsed: ",f6.3,"s")', endtime - starttime
   close(filenr)


   contains


   subroutine Triax_Step(stress, state, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
      stran, refstrain, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
      ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
      dfgrd1, noel, npt, layer, kspt, jstep, kinc, fak2, pressure_deviation, maxiter, breakall)
      ! ----------------------------------------------------------- !
      integer, intent(in) :: ndi, nshr, ntens, nstatv, nprops
      real(dp), dimension(nstatv), intent(inout) :: state
      real(dp), dimension(nprops), intent(in) :: materialparameters
      real(dp), dimension(ntens), intent(inout) :: stress, refstrain
      real(dp), dimension(ntens), intent(in) :: stran
      real(dp), dimension(ntens), intent(inout) :: ddsddt, drplde
      real(dp), dimension(ntens, ntens), intent(inout) :: ddsdde
      real(dp), dimension(3, 3), intent(in) :: drot, dfgrd0, dfgrd1
      real(dp), dimension(3), intent(in) :: coords
      real(dp), dimension(2), intent(in) :: time
      real(dp), dimension(1), intent(in) :: predef, dpred
      real(dp), intent(inout) :: sse, spd, scd,  rpl, drpldt, pnewdt
      real(dp), intent(in) :: temp, dtemp, celent, dt
      integer, dimension(4), intent(in) :: jstep
      integer, intent(in) :: noel, npt, layer, kspt, kinc
      character(len=80), intent(in) :: materialname
      real(dp), intent(in) :: fak2, pressure_deviation
      integer, intent(in) :: maxiter
      logical, intent(out) :: breakall
      ! ---
      real(dp), dimension(ntens) :: inoutstress1, inoutstress2, inpstrain1, inpstrain2
      real(dp), dimension(nstatv) :: inoutstate
      real(dp) :: diff1, diff2, modstrain
      integer :: strainidx, innercounter

      breakall = .False.
      strainidx = 0
   
      inoutstress1 = stress
      inoutstress2 = stress
      inpstrain1 = [refstrain(1), 0.0_dp, 0.0_dp, refstrain(4), refstrain(5), refstrain(6)]
      inoutstate = state                                             ! Reset state before call

      call UMAT(inoutstress1, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                stran, inpstrain1, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                dfgrd1, noel, npt, layer, kspt, jstep, kinc)

      diff1 = inoutstress1(2) - stress(2)

      inpstrain2 = [refstrain(1), fak2*refstrain(1), fak2*refstrain(1), &
                     refstrain(4), refstrain(5), refstrain(6)]
      inoutstate = state                                             ! Reset state before call
      call UMAT(inoutstress2, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                stran, inpstrain2, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                dfgrd1, noel, npt, layer, kspt, jstep, kinc)
      inoutstate = state                                             ! Reset state
      diff2 = inoutstress2(2) - stress(2)

      innercounter = 0
      minimize_difference : &
      do
         if (abs(diff2) < pressure_deviation) then
            exit minimize_difference
         end if

         if (innercounter > 10) then
            write(*, *) 'Strain increment halved'
            refstrain = refstrain/2.0_dp

            inoutstress1 = stress
            inoutstress2 = stress

            inpstrain1 = [refstrain(1), 0.0_dp, 0.0_dp, refstrain(4), refstrain(5), refstrain(6)]
            inoutstate = state                                       ! Reset state before call
            call UMAT(inoutstress1, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                      stran, inpstrain1, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                      ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                      dfgrd1, noel, npt, layer, kspt, jstep, kinc)
            diff1 = inoutstress1(2) - stress(2)

            inpstrain2 = [refstrain(1), fak2*refstrain(1), fak2*refstrain(1), &
                           refstrain(4), refstrain(5), refstrain(6)]
            inoutstate = state                                       ! Reset state before call
            call UMAT(inoutstress2, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                      stran, inpstrain2, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                      ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                      dfgrd1, noel, npt, layer, kspt, jstep, kinc)
            diff2 = inoutstress2(2) - stress(2)
            innercounter = 0
         end if

         modstrain = (diff2*inpstrain1(2) - diff1*inpstrain2(2))/(diff2 - diff1)
         inpstrain1 = inpstrain2
         diff1 = diff2
         inpstrain2(2:3) = modstrain

         inoutstress1 = stress
         inoutstate = state                                          ! Reset state before call
         call UMAT(inoutstress1, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                   stran, inpstrain2, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                   ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                   dfgrd1, noel, npt, layer, kspt, jstep, kinc)
         diff2 = inoutstress1(2) - stress(2)

         refstrain = inpstrain2
         innercounter = innercounter + 1
         strainidx = strainidx + 1

         ! Check for NaN entries
         if (diff2 /= diff2) then
            write(*, *) 'Error: NaN entries found'
            breakall = .True.
            exit minimize_difference
         end if
         if (strainidx > maxiter) then
            write(*, *) 'Error: Problem in triax loop'
            breakall = .True.
            exit minimize_difference
         end if
      end do minimize_difference

      stress = inoutstress1
      state = inoutstate
   end subroutine Triax_Step


   subroutine Processed_Arguments(materialname, triax_pressure, num_target_strains, target_strains, &
      num_params, materialparameters, voidratio, outfilename)
      real(dp), intent(out) :: triax_pressure
      integer, intent(out) :: num_target_strains
      real(dp), dimension(5), intent(out) :: target_strains
      integer, intent(out) :: num_params
      real(dp), dimension(16), intent(out) :: materialparameters
      real(dp), intent(out) :: voidratio
      character(len=80), intent(out) :: materialname, outfilename
      !
      character(len=80) :: temp
      integer :: status, num_arguments, idx, temp_num
 
      num_arguments = Command_Argument_Count()
      if (num_arguments < 8) then
         stop 'Expecting material name, triax pressure, number of and respective target strains, number of and ' &
            // 'respective material parameters, void ratio and log filename as argument'
      end if

      call get_command_argument(1, temp)
      materialname = trim(temp)

      call get_command_argument(2, temp)
      read(temp, *, iostat=status) triax_pressure
      if (status /= 0) then
         stop 'Error reading triax pressure (not float/integer?)'
      end if

      call get_command_argument(3, temp)
      read(temp, *, iostat=status) num_target_strains
      if (status /= 0) then
         stop 'Error reading number of target strains (not integer?)'
      end if
      if ((num_target_strains < 1) .or. (num_target_strains > 5)) then
         stop 'Number of target strains should be from one to five'
      end if
      if (num_arguments < 7 + num_target_strains) then
         stop 'Not enough arguments given'
      end if

      target_strains = 0.0_dp
      do idx = 1, num_target_strains
         call get_command_argument(3+idx, temp)
         read(temp, *, iostat=status) target_strains(idx)
         if (status /= 0) then
            stop 'Error reading element of target_strains (not float/integer?)'
         end if
      end do

      call get_command_argument(num_target_strains+4, temp)
      read(temp, *, iostat=status) num_params
      if (status /= 0) then
         stop 'Error reading number of parameters (not integer?)'
      end if
      if (num_params > 16) then
         stop 'More parameters given than expected (16)'
      end if
      if (num_arguments < 6 + num_target_strains + num_params) then
         stop 'Not enough arguments given'
      end if

      materialparameters = 0.0_dp
      do idx = 1, num_params
         call get_command_argument(num_target_strains+4+idx, temp)
         read(temp, *, iostat=status) materialparameters(idx)
         if (status /= 0) then
            stop 'Error reading element of materialparameters (not float/integer?)'
         end if
      end do

      call get_command_argument(num_arguments-1, temp)
      read(temp, *, iostat=status) voidratio
      if (status /= 0) then
         stop 'Error reading void ratio (not float/integer?)'
      end if

      call get_command_argument(num_arguments, temp)
      outfilename = trim(temp)
   end subroutine Processed_Arguments
end program Umat_Triax
