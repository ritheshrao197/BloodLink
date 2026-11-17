import { useEffect, useState } from 'react';
import { api } from '../lib/api';

const OTHER = '__other__';
let cache = null;

function useLocations() {
  const [states, setStates] = useState(cache);
  useEffect(() => {
    if (cache) return;
    api
      .locations()
      .then((d) => {
        cache = d.states;
        setStates(cache);
      })
      .catch(() => setStates([]));
  }, []);
  return states;
}

/**
 * State -> district (-> hospital) dropdowns, with "Other" free text at each level.
 * value: { state, city, hospital }; onChange receives the merged value.
 */
export default function LocationPicker({ value, onChange, withHospital = false, idPrefix = 'loc' }) {
  const states = useLocations();
  const [otherState, setOtherState] = useState(false);
  const [otherHospital, setOtherHospital] = useState(false);

  const stateObj = states?.find((s) => s.name === value.state);
  const districtObj = stateObj?.districts.find((d) => d.name === value.city);
  const set = (patch) => onChange({ ...value, ...patch });

  // Treat a pre-filled city we don't know as "Other" so it stays editable.
  useEffect(() => {
    if (states && value.city && !value.state) setOtherState(true);
  }, [states]); // eslint-disable-line react-hooks/exhaustive-deps

  const hospitalSelect = districtObj && !otherHospital && (!value.hospital || districtObj.hospitals.includes(value.hospital));

  return (
    <div className={withHospital ? 'grid gap-4 sm:grid-cols-3' : 'grid gap-4 sm:grid-cols-2'}>
      <div>
        <label className="label" htmlFor={`${idPrefix}-state`}>State</label>
        <select
          id={`${idPrefix}-state`}
          className="input"
          value={otherState ? OTHER : value.state || ''}
          onChange={(e) => {
            const other = e.target.value === OTHER;
            setOtherState(other);
            setOtherHospital(false);
            set({ state: other ? null : e.target.value, city: '', hospital: '' });
          }}
          required
        >
          <option value="" disabled>
            {states ? 'Select state' : 'Loading…'}
          </option>
          {states?.map((s) => (
            <option key={s.name}>{s.name}</option>
          ))}
          <option value={OTHER}>Other state…</option>
        </select>
      </div>

      <div>
        <label className="label" htmlFor={`${idPrefix}-district`}>{otherState ? 'City' : 'District'}</label>
        {otherState ? (
          <input id={`${idPrefix}-district`} className="input" value={value.city} placeholder="e.g. Hyderabad" onChange={(e) => set({ city: e.target.value })} required />
        ) : (
          <select
            id={`${idPrefix}-district`}
            className="input"
            value={value.city || ''}
            disabled={!stateObj}
            onChange={(e) => {
              setOtherHospital(false);
              set({ city: e.target.value, hospital: '' });
            }}
            required
          >
            <option value="" disabled>
              {stateObj ? 'Select district' : 'Pick a state first'}
            </option>
            {stateObj?.districts.map((d) => (
              <option key={d.name}>{d.name}</option>
            ))}
          </select>
        )}
      </div>

      {withHospital && (
        <div>
          <label className="label" htmlFor={`${idPrefix}-hospital`}>Hospital</label>
          {hospitalSelect ? (
            <select
              id={`${idPrefix}-hospital`}
              className="input"
              value={value.hospital || ''}
              onChange={(e) => {
                if (e.target.value === OTHER) {
                  setOtherHospital(true);
                  set({ hospital: '' });
                } else set({ hospital: e.target.value });
              }}
              required
            >
              <option value="" disabled>
                Select hospital
              </option>
              {districtObj.hospitals.map((h) => (
                <option key={h}>{h}</option>
              ))}
              <option value={OTHER}>Other hospital…</option>
            </select>
          ) : (
            <input
              id={`${idPrefix}-hospital`}
              className="input"
              value={value.hospital || ''}
              placeholder={districtObj || otherState ? 'Hospital name' : 'Pick a district first'}
              disabled={!districtObj && !otherState}
              onChange={(e) => set({ hospital: e.target.value })}
              required
            />
          )}
        </div>
      )}
    </div>
  );
}
