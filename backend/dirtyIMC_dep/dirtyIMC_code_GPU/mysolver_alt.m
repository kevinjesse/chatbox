function [UU, S, V]=soft_impute(GXobs,lambda,GXtest, maxk, maxiter, init_U, init_S, init_V, showopt)

if ~exist('showopt')
	showopt = 0;
end
[m n] = size(GXobs);
obj_vals=zeros(maxiter,1);
GXobs=sparse(GXobs);
[i_row, j_col, data]=find(GXobs); number_observed=length(data);
[i_row_test, j_col_test, data_test]=find(GXtest); number_observed_test=length(data_test);

if exist('init_U') == 0 || exist('init_S') == 0 || exist('init_V') == 0
	U=zeros(m,1); 
	V=zeros(n,1);
	S=zeros(1,1);
else
	U = init_U;
	V = init_V;
	S = init_S;
end

R = CompResidual(GXobs, (U*S)', V');
objval_old = norm(R,'fro')^2/2;
%obj = norm(R,'fro')^2/2 + lambda*sum(diag(S))
%tttemp=project_obs_UV(Glr_mat_u,Glr_mat_v,i_row,j_col,number_observed);
%GPmZ_old=sparse(i_row,j_col,tttemp,nrow,ncol,number_observed); 
%
%clear dim_check1 dim_check2 dim_check3
%
%tttemp=data-tttemp; train_err= tttemp'*tttemp;  
%soft_singvals=max(diag(Glr_mat_d)-lambda,0); 
%objval_old=train_err/2 + lambda*sum(soft_singvals);

i=0; 
%svd_rank=5;
timebegin = cputime;
timesvd = 0;
totaltime = 0;
timelist= [];
%oldV = [];
oldV = V;
klist = [];
anglelist = [];
U = U*S;
while (i<maxiter) 
	timebegin = cputime;
	i=i+1 ;
	if ~exist('showopt')
		fprintf('Iteration %g\n',i);
	end
	
	tbegin = cputime;
	kk = maxk;
	klist = [klist size(U,2)];
	[u,s,v] = randomsvd(R, U, V, m, n, kk, oldV, maxiter);
%	[u,s,v] = randomsvd(R, U, V, m, n, kk, oldV+randn(size(oldV))*1e-4, maxiter);
	oldV = v;
	sing_vals=diag(s); 
	clear s;
	timesvd = timesvd + cputime - tbegin;

	tmp=max(sing_vals-lambda,0);
	soft_singvals=tmp(tmp>0);
	no_singvals=length(soft_singvals);

	S = diag(soft_singvals);
	U = u(:,tmp>0); clear u;
	V = v(:,tmp>0); clear v;

	kk = size(U,2);
	Z = S;
	%kk
	
	%R = CompResidual(GXobs, (U*S)', V');
	%tmp_obj = norm(R,'fro')^2/2 + lambda*sum(diag(S))

	for inner = 1:2
		%% update S
		R = CompResidual(GXobs, (U*S)', V');
		objttt = norm(R,'fro')^2/2 + 0.5*lambda*trace(Z+(S*S')*inv(Z));
		if showopt ~= 0
			fprintf('obj inner %g before S update: %g\n',inner, objttt);
		end
		
		A = inv(Z);
		AA = A+A';
		grad =  U'*R*V - 0.5*lambda*(AA)*S;
		xx = zeros(kk,kk);
		r = grad;
		p = r;
		k = 0;
		rnorm = norm(r,'fro')^2;
		init_rnorm = rnorm;
		for cgiter = 1:4
%			DUT = p*(U');
%			VDUT_Omega = CompProduct(GXobs', V', DUT);
			DUT = p*(V');
			VDUT_Omega = CompProduct(GXobs, U', DUT);
			Ap = U'*VDUT_Omega*V+0.5*lambda*(p*AA);
%			Ap = V'*VDUT_Omega*U+ 0.5*lambda*(p*AA);
			if norm(r, 'fro') == 0
				alpha = 0;
			else
				alpha = norm(r,'fro')^2/(sum(sum(p.*Ap)));
			end
			xx = xx + alpha*p;
			r = r-alpha*Ap;
			rnorm_new = norm(r,'fro')^2;
			if showopt ~= 0
				fprintf('Inner iter %g, residual norm: %g\n', cgiter, rnorm_new);
			end
			if ( rnorm_new <= init_rnorm*1e-4)
				break;
			end
			beta = rnorm_new/rnorm;
			rnorm = rnorm_new;
			p = r+beta*p;
		end
		S = S + xx;
		%norm(S - S')

%		R = CompResidual(GXobs, (U*S)', V');
%		objttt = norm(R,'fro')^2/2 + 0.5*lambda*trace(Z+(S*S')*inv(Z));
%		fprintf('obj inner %g after S update: %g\n',inner, objttt);

		%% Update Z
		[mogou mogos mogov] = svd(S*S');
		Z = mogou*diag(sqrt(diag(mogos)))*mogou';
%		Z = (sqrt(S*S'));
		if(isreal(Z) == 0)
			keyboard;
		end
%		R = CompResidual(GXobs, (U*S)', V');
%		objttt = norm(R,'fro')^2/2 + 0.5*lambda*trace(Z+(S*S')*inv(Z));
%		fprintf('obj inner %g after Z update: %g\n',inner, objttt);

	end

	[u s v] = svd(S);
	if(isreal(u) == 0 || isreal(v) == 0)
		fprintf('not real...\n');
	end
	U=U*u(:,1:kk);
	V=V*v(:,1:kk);
	S = s(1:kk,1:kk);

	totaltime = totaltime + cputime - timebegin;
	timelist(i) = totaltime;

	UU = U;
	U = U*S;
	[uuuu ssss vvvv] = svd(S);

%	tttemp=project_obs_UV(U,V,i_row,j_col,number_observed);
%	tttemp=data-tttemp;
%	train_err= tttemp'*tttemp; 

	R = CompResidual(GXobs, U', V');
	train_err = norm(R,'fro')^2;

%	objval_new=train_err/2 + lambda*sum(soft_singvals);
%	objval_new=train_err/2 + lambda*sum(inner_singvalues);
	objval_new = train_err/2 + lambda*sum(diag(ssss));
	obj_vals(i)=objval_new;
	%objval_new
	objval_old=objval_new;

%	[uuu sss vvv] = svd(S);
%	grad = uu'*R*V - lambda*uuu*vvv';
%	fprintf('norm of gradient: %g\n', norm(grad,'fro'));

	if numel(i_row_test) > 0
	tttemp_test=project_obs_UV(U,V,i_row_test,j_col_test,number_observed_test);
	tttemp_test =  tttemp_test-data_test;
	test_err = sqrt(tttemp_test'*tttemp_test/numel(data_test));
	test_rmses(i) = test_err;
	%test_err
end
end

%obj_vals=obj_vals(1:i);
%test_rmses = test_rmses(1:i);
%klist
