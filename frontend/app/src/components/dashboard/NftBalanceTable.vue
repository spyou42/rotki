<template>
  <card v-if="balances.length > 0" outlined-body>
    <template #title>
      {{ $t('nft_balance_table.title') }}
      <v-btn :to="nonFungibleRoute" icon class="ml-2">
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </template>
    <template #details>
      <v-menu
        id="nft_balance_table__column-filter"
        transition="slide-y-transition"
        max-width="250px"
        offset-y
      >
        <template #activator="{ on }">
          <menu-tooltip-button
            :tooltip="$t('dashboard_asset_table.select_visible_columns')"
            class-name="ml-4 nft_balance_table__column-filter__button"
            :on-menu="on"
          >
            <v-icon>mdi-dots-vertical</v-icon>
          </menu-tooltip-button>
        </template>
        <visible-columns-selector group="NFT" />
      </v-menu>
    </template>
    <data-table :headers="tableHeaders" :items="balances" sort-by="usdPrice">
      <template #item.name="{ item }">
        {{ item.name ? item.name : item.id }}
      </template>
      <template #item.priceInAsset="{ item }">
        <amount-display
          v-if="item.priceAsset !== currency"
          :value="item.priceInAsset"
          :asset="item.priceAsset"
        />
        <span v-else>-</span>
      </template>
      <template #item.usdPrice="{ item }">
        <amount-display
          :value="item.usdPrice"
          show-currency="symbol"
          fiat-currency="USD"
        />
      </template>
      <template #item.percentageOfTotalNetValue="{ item }">
        <percentage-display :value="percentageOfTotalNetValue(item.usdPrice)" />
      </template>
      <template #item.percentageOfTotalCurrentGroup="{ item }">
        <percentage-display :value="percentageOfCurrentGroup(item.usdPrice)" />
      </template>
      <template #body.append="{ isMobile }">
        <tr v-if="!isMobile" class="font-weight-medium">
          <td colspan="2">
            {{ $t('nft_balance_table.row.total') }}
          </td>
          <td class="text-end">
            <amount-display
              :value="total"
              show-currency="symbol"
              fiat-currency="USD"
            />
          </td>
          <td
            v-if="tableHeaders.length - 3"
            :colspan="tableHeaders.length - 3"
          />
        </tr>
        <tr v-else class="font-weight-medium">
          <td
            class="d-flex align-center justify-space-between font-weight-medium"
          >
            <div>
              {{ $t('nft_balance_table.row.total') }}
            </div>
            <div>
              <amount-display
                :value="total"
                show-currency="symbol"
                fiat-currency="USD"
              />
            </div>
          </td>
        </tr>
      </template>
    </data-table>
  </card>
</template>

<script lang="ts">
import { BigNumber } from '@rotki/common';
import { computed, defineComponent, Ref } from '@vue/composition-api';
import { DataTableHeader } from 'vuetify';
import VisibleColumnsSelector from '@/components/dashboard/VisibleColumnsSelector.vue';
import MenuTooltipButton from '@/components/helper/MenuTooltipButton.vue';
import { currency } from '@/composables/session';
import { setupSettings } from '@/composables/settings';
import i18n from '@/i18n';
import { Routes } from '@/router/routes';
import { BalanceActions } from '@/store/balances/action-types';
import { NonFungibleBalance } from '@/store/balances/types';
import { useStore } from '@/store/utils';
import {
  DashboardTablesVisibleColumns,
  DashboardTableType
} from '@/types/frontend-settings';
import { TableColumn } from '@/types/table-column';
import { Zero } from '@/utils/bignumbers';

const tableHeaders = (
  currency: Ref<string>,
  dashboardTablesVisibleColumns: Ref<DashboardTablesVisibleColumns>
) => {
  return computed<DataTableHeader[]>(() => {
    const visibleColumns =
      dashboardTablesVisibleColumns.value[DashboardTableType.NFT];

    const headers: DataTableHeader[] = [
      {
        text: i18n.t('nft_balance_table.column.name').toString(),
        value: 'name',
        cellClass: 'text-no-wrap'
      },
      {
        text: i18n.t('nft_balance_table.column.price_in_asset').toString(),
        value: 'priceInAsset',
        align: 'end',
        width: '75%',
        class: 'text-no-wrap'
      },
      {
        text: i18n
          .t('nft_balance_table.column.price', {
            currency: currency.value
          })
          .toString(),
        value: 'usdPrice',
        align: 'end',
        class: 'text-no-wrap'
      }
    ];

    if (visibleColumns.includes(TableColumn.PERCENTAGE_OF_TOTAL_NET_VALUE)) {
      headers.push({
        text: i18n.t('nft_balance_table.column.percentage').toString(),
        value: 'percentageOfTotalNetValue',
        align: 'end',
        class: 'text-no-wrap'
      });
    }

    if (
      visibleColumns.includes(TableColumn.PERCENTAGE_OF_TOTAL_CURRENT_GROUP)
    ) {
      headers.push({
        text: i18n
          .t(
            'dashboard_asset_table.headers.percentage_of_total_current_group',
            {
              group: 'NFT'
            }
          )
          .toString(),
        value: 'percentageOfTotalCurrentGroup',
        align: 'end',
        class: 'text-no-wrap'
      });
    }

    return headers;
  });
};

export default defineComponent({
  name: 'NftBalanceTable',
  components: { VisibleColumnsSelector, MenuTooltipButton },
  setup() {
    const store = useStore();
    const balances = computed<NonFungibleBalance[]>(
      () => store.getters['balances/nfBalances']
    );

    const totalNetWorthUsd = computed<BigNumber>(
      () => store.getters['statistics/totalNetWorthUsd']
    );

    const calculatePercentage = (value: BigNumber, divider: BigNumber) => {
      return value.div(divider).multipliedBy(100).toFixed(2);
    };

    const percentageOfTotalNetValue = (value: BigNumber) => {
      return calculatePercentage(value, totalNetWorthUsd.value);
    };

    const percentageOfCurrentGroup = (value: BigNumber) => {
      return calculatePercentage(value, total.value);
    };

    const refresh = async () => {
      return await store.dispatch(
        `balances/${BalanceActions.FETCH_NF_BALANCES}`,
        true
      );
    };

    const total = computed(() => {
      return balances.value.reduce(
        (sum, value) => sum.plus(value.usdPrice),
        Zero
      );
    });

    const { dashboardTablesVisibleColumns } = setupSettings();

    return {
      balances,
      tableHeaders: tableHeaders(currency, dashboardTablesVisibleColumns),
      currency,
      refresh,
      total,
      nonFungibleRoute: Routes.NON_FUNGIBLE,
      percentageOfTotalNetValue,
      percentageOfCurrentGroup
    };
  }
});
</script>
