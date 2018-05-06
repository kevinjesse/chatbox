TmpXa = full(mmread("sparseXgenre.mm.mtx"));
TmpYa = full(mmread("sparseYgenre.mm.mtx"));
% 
TmpXc = full(mmread("sparseXactor.mm.mtx"));
TmpYc = full(mmread("sparseYactor.mm.mtx"));
%TmpX = [TmpX./3 TmpXa./3];
% TmpX = TmpX(:,1:200);

% TmpY = TmpY(:,1:200);
%TmpY = [TmpY./3 TmpYa./3];
% % 
TmpXb = full(mmread("sparseXmpaa.mm.mtx"));
TmpX = [TmpXa TmpXb TmpXc]./3;
TmpYb = full(mmread("sparseYmpaa.mm.mtx"));
TmpY = [TmpYa TmpYb TmpYc]./3;

TmpX(isnan(TmpX))=0; TmpX(isinf(TmpX))=0;
TmpY(isnan(TmpY))=0; TmpY(isinf(TmpY))=0;

[j,k] = size(TmpX);
[s,t] = size(TmpY);

Obs = mmread("sparseN.mm.mtx");
Obs = Obs';
[m,n] = size(Obs);

DCG_SIZE = 10;

[~,ci] = sort(Obs, 2, 'descend');
Obs_i = zeros(m, n);
Obs_rel = zeros(m, n);
ObsCF_i = zeros(m, n);
ObsCF_rel = zeros(m, n);
% 
for i = 1:m
    rel = DCG_SIZE;
    for ii = 1:DCG_SIZE
        Obs_i(i, ci(i, ii)) = ii;
        Obs_rel(i, ci(i, ii)) = rel;
        rel = rel - 1;
    end
end

%Maximum match
for user = 1:j
    kept = 0;
    parfor movie = 1:s
        [~,I1] = max(TmpXc(user,:));
        [~,I2] = max(TmpYc(movie,:));
        if I1 == I2
             [~,I1] = max(TmpXa(user,:));
             [~,I2] = max(TmpYa(movie,:));
             if I1 == I2
                  %fprintf("genre match! user: %d AND movie: %d\n", user, movie);
                [~,I1] = max(TmpXb(user,:));
                [~,I2] = max(TmpYb(movie,:));
                if I1 == I2
                    kept = kept + 1;
                    continue;
                    %fprintf("mpaa match! user: %d AND movie: %d\n", user, movie);
                    fprintf("all match! user: %d AND movie: %d\n", user, movie);
                end
             end
            %fprintf("person match! user: %d AND movie: %d\n", user, movie);
        end
        Obs(user, movie) = -1;
    end
    [~,ci] = sort(Obs(user, :), 2, 'descend');
 
    rel = DCG_SIZE;
    for ii = 1:DCG_SIZE
        ObsCF_i(user, ci(ii)) = ii;
        if ii>kept 
            ObsCF_rel(user, ci(ii)) = rel;
        else
            ObsCF_rel(user, ci(ii)) = rel;
            rel = rel - 1;
        end

    end
    %criteria_DCG_R = dcg(ObsCF_rel(user,:), Obs_i(user,:));
    %break;
end

criteria_DCG_R = dcg(ObsCF_rel, Obs_i);
% 
% 
