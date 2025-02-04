import { ActionResult } from '@rotki/common/lib/data';
import {
  GitcoinGrantEventsPayload,
  GitcoinGrantReport,
  GitcoinReportPayload
} from '@rotki/common/lib/gitcoin';
import {
  AxiosInstance,
  AxiosRequestTransformer,
  AxiosResponseTransformer
} from 'axios';
import {
  axiosSnakeCaseTransformer,
  getUpdatedKey,
  setupTransformer
} from '@/services/axios-tranformers';
import {
  balanceAxiosTransformer,
  basicAxiosTransformer
} from '@/services/consts';
import { IgnoredActions, tradeNumericKeys } from '@/services/history/const';
import {
  LedgerActionResult,
  NewTrade,
  Trade,
  TradeLocation,
  TransactionRequestPayload,
  Transactions
} from '@/services/history/types';
import {
  EntryWithMeta,
  LimitedResponse,
  PendingTask
} from '@/services/types-api';
import {
  handleResponse,
  validStatus,
  validWithParamsSessionAndExternalService,
  validWithSessionStatus
} from '@/services/utils';
import { LedgerAction } from '@/store/history/types';
import { ReportProgress } from '@/store/reports/types';

export class HistoryApi {
  private readonly axios: AxiosInstance;
  private readonly responseTransformer: AxiosResponseTransformer[] =
    setupTransformer(tradeNumericKeys);
  private readonly requestTransformer: AxiosRequestTransformer[];

  constructor(axios: AxiosInstance) {
    this.axios = axios;
    this.requestTransformer = [axiosSnakeCaseTransformer].concat(
      axios.defaults.transformRequest as AxiosRequestTransformer[]
    );
  }

  async trades(
    location?: TradeLocation,
    onlyCache?: boolean
  ): Promise<PendingTask> {
    const params = {
      asyncQuery: true,
      onlyCache: onlyCache ? onlyCache : undefined,
      location
    };
    return this.axios
      .get<ActionResult<PendingTask>>('/trades', {
        params: axiosSnakeCaseTransformer(params),
        validateStatus: validStatus,
        transformResponse: this.responseTransformer
      })
      .then(handleResponse);
  }

  async addExternalTrade(trade: NewTrade): Promise<Trade> {
    return this.axios
      .put<ActionResult<Trade>>('/trades', trade, {
        validateStatus: validStatus,
        transformResponse: this.responseTransformer,
        transformRequest: this.requestTransformer
      })
      .then(handleResponse);
  }

  async editExternalTrade(trade: Trade): Promise<Trade> {
    return this.axios
      .patch<ActionResult<Trade>>('/trades', trade, {
        validateStatus: validStatus,
        transformResponse: this.responseTransformer,
        transformRequest: this.requestTransformer
      })
      .then(handleResponse);
  }

  async deleteExternalTrade(tradeId: string): Promise<boolean> {
    return this.axios
      .delete<ActionResult<boolean>>('/trades', {
        data: axiosSnakeCaseTransformer({ tradeId }),
        validateStatus: validStatus
      })
      .then(handleResponse);
  }

  async assetMovements(
    location?: TradeLocation,
    onlyCache?: boolean
  ): Promise<any> {
    const params = {
      asyncQuery: true,
      onlyCache: onlyCache ? onlyCache : undefined,
      location
    };
    return this.axios
      .get<ActionResult<PendingTask>>('/asset_movements', {
        params: axiosSnakeCaseTransformer(params),
        validateStatus: validWithParamsSessionAndExternalService,
        transformResponse: setupTransformer([])
      })
      .then(handleResponse);
  }

  private internalEthTransactions<T>(
    payload: TransactionRequestPayload,
    async: boolean
  ): Promise<T> {
    let url = `/blockchains/ETH/transactions`;
    const { address, ...data } = payload;
    if (address) {
      url += `/${address}`;
    }
    return this.axios
      .get<ActionResult<T>>(url, {
        params: axiosSnakeCaseTransformer({
          asyncQuery: async,
          ...data,
          orderByAttribute: getUpdatedKey(payload.orderByAttribute, false)
        }),
        validateStatus: validWithParamsSessionAndExternalService,
        transformResponse: basicAxiosTransformer
      })
      .then(handleResponse);
  }

  async ethTransactionsTask(
    payload: TransactionRequestPayload
  ): Promise<PendingTask> {
    return this.internalEthTransactions<PendingTask>(payload, true);
  }

  async ethTransactions(
    payload: TransactionRequestPayload
  ): Promise<Transactions> {
    const ethTransactions = await this.internalEthTransactions<Transactions>(
      payload,
      false
    );
    return Transactions.parse(ethTransactions);
  }

  async ledgerActions(
    start: number = 0,
    end: number | undefined = undefined,
    location: string | undefined = undefined,
    onlyCache?: boolean
  ): Promise<PendingTask> {
    return this.axios
      .get<ActionResult<PendingTask>>(`/ledgeractions`, {
        params: axiosSnakeCaseTransformer({
          asyncQuery: true,
          fromTimestamp: start,
          toTimestamp: end ? end : undefined,
          location: location ? location : undefined,
          onlyCache: onlyCache ? onlyCache : undefined
        }),
        validateStatus: validStatus,
        transformResponse: basicAxiosTransformer
      })
      .then(handleResponse);
  }

  async addLedgerAction(
    action: Omit<LedgerAction, 'identifier'>
  ): Promise<LedgerActionResult> {
    return this.axios
      .put<ActionResult<LedgerActionResult>>(
        '/ledgeractions',
        axiosSnakeCaseTransformer(action),
        {
          validateStatus: validStatus,
          transformResponse: balanceAxiosTransformer
        }
      )
      .then(handleResponse);
  }

  async editLedgerAction(
    action: LedgerAction
  ): Promise<LimitedResponse<EntryWithMeta<LedgerAction>>> {
    return this.axios
      .patch<ActionResult<LimitedResponse<EntryWithMeta<LedgerAction>>>>(
        '/ledgeractions',
        axiosSnakeCaseTransformer({ action }),
        {
          validateStatus: validStatus,
          transformResponse: balanceAxiosTransformer
        }
      )
      .then(handleResponse);
  }

  async deleteLedgerAction(
    identifier: number
  ): Promise<LimitedResponse<EntryWithMeta<LedgerAction>>> {
    return this.axios
      .delete<ActionResult<LimitedResponse<EntryWithMeta<LedgerAction>>>>(
        '/ledgeractions',
        {
          data: axiosSnakeCaseTransformer({ identifier }),
          validateStatus: validStatus,
          transformResponse: balanceAxiosTransformer
        }
      )
      .then(handleResponse);
  }

  async getProgress(): Promise<ReportProgress> {
    return this.axios
      .get<ActionResult<ReportProgress>>(`/history/status`, {
        validateStatus: validWithSessionStatus,
        transformResponse: basicAxiosTransformer
      })
      .then(handleResponse);
  }

  async gatherGitcoinGrandEvents(
    payload: GitcoinGrantEventsPayload
  ): Promise<PendingTask> {
    return this.axios
      .post<ActionResult<PendingTask>>(
        '/gitcoin/events',
        axiosSnakeCaseTransformer({ ...payload, asyncQuery: true }),
        {
          validateStatus: validStatus,
          transformResponse: balanceAxiosTransformer
        }
      )
      .then(handleResponse);
  }

  async deleteGitcoinGrantEvents(grantId: number): Promise<boolean> {
    return this.axios
      .delete<ActionResult<boolean>>('/gitcoin/events', {
        data: axiosSnakeCaseTransformer({ grantId }),
        validateStatus: validStatus
      })
      .then(handleResponse);
  }

  async generateReport(
    payload: GitcoinReportPayload
  ): Promise<GitcoinGrantReport> {
    return this.axios
      .put<ActionResult<GitcoinGrantReport>>('/gitcoin/report', payload, {
        validateStatus: validStatus,
        transformResponse: setupTransformer(['total', 'amount', 'value']),
        transformRequest: this.requestTransformer
      })
      .then(handleResponse);
  }

  fetchIgnored(): Promise<IgnoredActions> {
    return this.axios
      .get<ActionResult<IgnoredActions>>('/actions/ignored', {
        validateStatus: validStatus,
        transformResponse: setupTransformer([])
      })
      .then(handleResponse)
      .then(result => IgnoredActions.parse(result));
  }
}
