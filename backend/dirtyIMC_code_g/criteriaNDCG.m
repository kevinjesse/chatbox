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



Obs = mmread("sparseN.mm.mtx");
Obs = Obs';
% Obs = Obs(1:100,:);
% TmpXa = TmpXa(1:100,:);
% TmpYa = TmpYa(1:100,:);
% TmpXb = TmpXb(1:100,:);
% TmpYb = TmpYb(1:100,:);
% TmpXc = TmpXc(1:100,:);
% TmpYc = TmpYc(1:100,:);

[j,k] = size(TmpXa);
[s,t] = size(TmpYa);
[m,n] = size(Obs);

DCG_SIZE = n;

Obs_temp = Obs;
Obs_i = zeros(m, n);
Obs_rel = zeros(m, n);
ObsCF_i = zeros(m, n);
ObsCF_rel = zeros(m, n);
% 
% for i = 1:m
%     rel = DCG_SIZE;
%     for ii = 1:DCG_SIZE
%         Obs_i(i, ci(i, ii)) = ii;
%         Obs_rel(i, ci(i, ii)) = rel;
%         if ii>1 && Obs(i,ci(i,ii-1)) ~= Obs(i,ci(i,ii))
%             rel = rel - 1;
%         end
%     end
% end
% 
% Obs_DCG_R = dcg(Obs_rel,Obs_i);

%Maximum match
for user = 1:j
    fprintf("At user: %d\n", user);
    kept = 0;
    parfor movie = 1:s

        [~,I1] = max(TmpXc(user,:));
        exists = TmpYc(movie,I1) > 0;
        if exists
%              [~,I1] = max(TmpXa(user,:));
%              exists = TmpYa(movie,I1) > 0;
%              if exists
%                   [~,I1] = max(TmpXb(user,:));
%                   exists = TmpYb(movie,I1) > 0;
                  %fprintf("genre match! user: %d AND movie: %d\n", user, movie);

                  if exists
                      kept = kept + 1;
                      continue;
                    %fprintf("mpaa match! user: %d AND movie: %d\n", user, movie);
                      fprintf("all match! user: %d AND movie: %d\n", user, movie);
                   end
            % end
            %fprintf("person match! user: %d AND movie: %d\n", user, movie);
        end
        Obs_temp(user, movie) = -1;
    end
    [~,ci] = sort(Obs_temp(user, :), 2, 'descend');
    %[~,cio] = sort(Obs(user, :), 2, 'descend');
    
 
    rel = DCG_SIZE;
    for ii = 1:DCG_SIZE
        %Obs_i(user, cio(ii)) = ii;
        ObsCF_i(user, ci(ii)) = ii;

        ObsCF_rel(user, ci(ii)) = rel;
        %Obs_rel(user, cio(ii)) = rel;
        if ii<=kept
%             if ii<DCG_SIZE && Obs_temp(user,ci(ii+1)) == Obs_temp(user,ci(ii))
%                  continue
%             end
            rel = rel - 1;
        else
            rel = kept;
        end

    end
    %criteria_DCG_R = dcg(ObsCF_rel(user,:), Obs_i(user,:));
    %Obs_DCG_R = dcg(Obs_rel(user,:),Obs_i(user, :));
    %CRITICAL_NDCG = criteria_DCG_R./Obs_DCG_R;
end

[~,ci] = sort(Obs, 2, 'descend');
for i = 1:m
    rel = DCG_SIZE;
    for ii = 1:DCG_SIZE
        Obs_i(i, ci(i, ii)) = ii;
        Obs_rel(i, ci(i, ii)) = rel;
        if ii>1 && Obs(i,ci(i,ii-1)) ~= Obs(i,ci(i,ii))
        %if ii>1 && Obs(i,ci(i,ii-1)) ~= Obs(i,ci(i,ii))
            rel = rel - 1;
        end
    end
end

Obs_DCG_R = dcg(Obs_rel,Obs_i);

criteria_DCG_R = dcg(ObsCF_rel, Obs_i);
CRITICAL_NDCG = mean(criteria_DCG_R./Obs_DCG_R);
% 
% 
