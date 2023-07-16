program Oedo_pert_test
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
   real(dp), dimension(nstatv) :: statevariables, inoutstate
   real(dp), dimension(ntens) :: stress, inoutstress
   real(dp), dimension(ntens) :: strain, inpstrain
   real(dp), dimension(10) :: oedo_pressures
   real(dp) :: dt, sigma1, voidratio, numbersign
   integer :: istep, idx, filenr, stat, ixx, jxx, num_params, num_pressures
   integer, parameter :: maxiter = 50000
   logical :: breakall, is_success
   real(dp) :: starttime, endtime, K0

   call Processed_Arguments(materialname=materialname, num_pressures=num_pressures, &
      oedo_pressures=oedo_pressures, num_params=num_params, materialparameters=materialparameters, &
      voidratio=voidratio, outfilename=outfilename)

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
   dt = 0.00001_dp

   ! Give initial stress and strain matrices (in vector form)
   sigma1 = oedo_pressures(1)
   K0 = 0.5_dp
   stress = [K0*sigma1, sigma1, K0*sigma1, 0.0_dp, 0.0_dp, 0.0_dp]
   strain = [0.0_dp, -1.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]*dt
   statevariables = 0.0_dp
   statevariables(1) = voidratio
   statevariables(3) = -0.0001

   filenr = 20
   open(filenr, file=trim(outfilename), iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   ! Write output for start point as well
   write(filenr, '(f13.6, a, f13.6)') -stress(2), '   ', voidratio

   inoutstress = stress
   inoutstate = statevariables
   idx = 1
   breakall = .False.
   
   call cpu_time(starttime)
   loading_cycle: &
   do istep = 2, num_pressures
      numbersign = (-1.0_dp)**istep
      inpstrain = numbersign*strain
      loading_loop: &
      do
         if (numbersign*inoutstress(2) < numbersign*oedo_pressures(istep)) then
            exit loading_loop
         end if
         call UMAT(inoutstress, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                   stran, inpstrain, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                   ntens, nstatv, materialparameters(1:num_params), num_params, coords, drot, &
                   pnewdt, celent, dfgrd0, dfgrd1, noel, npt, layer, kspt, jstep, kinc)

         write(filenr, '(f13.6, a, f13.6)') -inoutstress(2), '   ', inoutstate(1)

         ! No Assignment necessary: inoutstress and inoutstate are automatically reassigned in UMAT-call
         idx = idx + 1
         if (idx > maxiter) then
            write(*, *) 'Maximum number of specified iterations reached'
            breakall = .True.
            exit loading_loop
         end if
      end do loading_loop
      if (breakall) then
         exit loading_cycle
      end if
   end do loading_cycle

   call cpu_time(endtime)
   print '("Elapsed: ",f6.3,"s")', endtime - starttime
   close(filenr)


   contains


   subroutine Processed_Arguments(materialname, num_pressures, oedo_pressures, num_params, materialparameters, &
      voidratio, outfilename)
      integer, intent(out) :: num_pressures
      real(dp), dimension(10), intent(out) :: oedo_pressures
      integer, intent(out) :: num_params
      real(dp), dimension(16), intent(out) :: materialparameters
      real(dp), intent(out) :: voidratio
      character(len=80), intent(out) :: materialname, outfilename
      !
      character(len=80) :: temp
      integer :: status, num_arguments, idx, temp_num

      num_arguments = Command_Argument_Count()
      if (num_arguments < 7) then
         stop 'Expecting material name, number of and respective oedo pressures, number of and ' &
            // 'respective material parameters, void ratio and log filename as argument'
      end if

      call get_command_argument(1, temp)
      materialname = trim(temp)

      call get_command_argument(2, temp)
      read(temp, *, iostat=status) num_pressures
      if (status /= 0) then
         stop 'Error reading number of pressures (not integer?)'
      end if
      if ((num_pressures < 1) .or. (num_pressures > 10)) then
         stop 'Number of oedo pressures should be from one to ten'
      end if
      if (num_arguments < 6 + num_pressures) then
         stop 'Not enough arguments given'
      end if

      oedo_pressures = 0.0_dp
      do idx = 1, num_pressures
         call get_command_argument(2+idx, temp)
         read(temp, *, iostat=status) oedo_pressures(idx)
         if (status /= 0) then
            stop 'Error reading element of oedo_pressure (not float/integer?)'
         end if
      end do

      call get_command_argument(num_pressures+3, temp)
      read(temp, *, iostat=status) num_params
      if (status /= 0) then
         stop 'Error reading number of parameters (not integer?)'
      end if
      if (num_params > 16) then
         stop 'More parameters given than expected (16)'
      end if
      if (num_arguments < 5 + num_pressures + num_params) then
         stop 'Not enough arguments given'
      end if

      materialparameters = 0.0_dp
      do idx = 1, num_params
         call get_command_argument(num_pressures+3+idx, temp)
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
end program Oedo_pert_test
